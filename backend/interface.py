# interface.py

from backend.zotero_dbase import ZoteroLibrary
from backend.zoteroitem import ZoteroItem
from backend.pdf import PDF
from backend.vector_db import ChromaClient
from backend.embed_utils import get_embedding, rerank_passages
from backend.local_llm import generate_answer
import os
from collections import OrderedDict
import threading
import time

class ZoteroChatbot:
    def __init__(self, db_path, chroma_path):
        self.zlib = ZoteroLibrary(db_path)
        self.chroma = ChromaClient(chroma_path)
        # Indexing state for reporting progress via /index_status
        self.is_indexing = False
        # Cancellation flag for background indexing
        self._cancel_indexing = False
        # Optional: simple progress counter (chunks processed)
        self.index_progress = {
            "processed_items": 0,
            "total_items": 0,
            "start_time": None,
            "elapsed_seconds": 0,
            "eta_seconds": None,
        }
        self._index_thread = None
    
    def _index_library_worker(self):
        try:
            start_time = time.time()
            self.index_progress["start_time"] = start_time
            
            raw_items = self.zlib.search_parent_items_with_pdfs()
            self.index_progress["total_items"] = len(raw_items)
            self.index_progress["processed_items"] = 0
            items = [ZoteroItem(filepath=it['pdf_path'], metadata=it) for it in raw_items]

            # Extract text for each item using PDF logic with page numbers
            for item in items:
                if self._cancel_indexing:
                    break
                if not (item.filepath and os.path.exists(item.filepath)):
                    self.index_progress["processed_items"] += 1
                    continue  # Skip missing or inaccessible PDFs
                pdf = PDF(item.filepath)
                # Use page-aware extraction
                pages_data = pdf.extract_text_with_pages()
                # Store page data for later chunking
                item.metadata['pages_data'] = pages_data
                # Also store concatenated text for backward compatibility
                text = "\n\n".join([p['text'] for p in pages_data])
                item.metadata['text'] = text if text else ""

            # Vectorize each item's text (chunk/embedding logic with page tracking)
            for item in items:
                if self._cancel_indexing:
                    break
                pages_data = item.metadata.get('pages_data') or []
                if not pages_data:
                    self.index_progress["processed_items"] += 1
                    continue
                
                # Chunk with page awareness
                chunks_with_pages = self.chunk_text_with_pages(pages_data)
                if not chunks_with_pages:
                    self.index_progress["processed_items"] += 1
                    continue
                
                chunks = [c['text'] for c in chunks_with_pages]
                vectors = [get_embedding(chunk) for chunk in chunks]
                
                # Validate embedding dimensions
                if vectors and len(vectors[0]) != 768:
                    print(f"WARNING: Unexpected embedding dimension {len(vectors[0])} for item {item.metadata.get('item_id')}")

                # Generate unique chunk IDs
                item_id = str(item.metadata.get('item_id'))
                chunk_ids = [f"{item_id}:{i}" for i in range(len(chunks))]

                # Sanitize metadata per chunk to primitives, no None
                meta_src = item.metadata
                title = meta_src.get("title") or ""
                authors = meta_src.get("authors") or ""
                tags = meta_src.get("tags") or ""
                collections = meta_src.get("collections") or ""
                year = meta_src.get("date") or ""
                pdf_path = meta_src.get("pdf_path") or ""

                metas = []
                for i, chunk_info in enumerate(chunks_with_pages):
                    metas.append({
                        "item_id": item_id,
                        "chunk_idx": int(i),
                        "title": title,
                        "authors": authors,
                        "tags": tags,
                        "collections": collections,
                        "year": year,
                        "pdf_path": pdf_path,
                        "page": chunk_info['page'],  # Add page number!
                    })

                self.chroma.add_chunks(
                    ids=chunk_ids,
                    documents=chunks,
                    metadatas=metas,
                    embeddings=vectors
                )
                # Update progress after processing this item
                self.index_progress["processed_items"] += 1
                
                # Calculate time estimates
                elapsed = time.time() - self.index_progress["start_time"]
                self.index_progress["elapsed_seconds"] = int(elapsed)
                
                processed = self.index_progress["processed_items"]
                total = self.index_progress["total_items"]
                if processed > 0 and total > 0:
                    avg_time_per_item = elapsed / processed
                    remaining_items = total - processed
                    self.index_progress["eta_seconds"] = int(avg_time_per_item * remaining_items)
                
                # small sleep to allow cancellation to be checked promptly in CPU-bound loops
                time.sleep(0)
            
            # Build BM25 index after adding all chunks
            print("Building BM25 index for sparse retrieval...")
            self.chroma.build_bm25_index()
        finally:
            self.is_indexing = False
            self._cancel_indexing = False

    def _index_library_incremental_worker(self):
        """Index only new items that aren't already in the database."""
        try:
            start_time = time.time()
            self.index_progress["start_time"] = start_time
            
            # Get all items from Zotero
            raw_items = self.zlib.search_parent_items_with_pdfs()
            all_item_ids = {str(it['item_id']) for it in raw_items}
            
            # Get already indexed item IDs
            indexed_ids = self.chroma.get_indexed_item_ids()
            
            # Find new items
            new_item_ids = all_item_ids - indexed_ids
            
            # Filter to only new items
            new_items_data = [it for it in raw_items if str(it['item_id']) in new_item_ids]
            
            self.index_progress["total_items"] = len(new_items_data)
            self.index_progress["processed_items"] = 0
            self.index_progress["skipped_items"] = len(indexed_ids)
            
            if len(new_items_data) == 0:
                print("No new items to index.")
                return
            
            print(f"Found {len(new_items_data)} new items to index (skipping {len(indexed_ids)} already indexed)")
            
            items = [ZoteroItem(filepath=it['pdf_path'], metadata=it) for it in new_items_data]

            # Extract text for each new item
            for item in items:
                if self._cancel_indexing:
                    break
                if not (item.filepath and os.path.exists(item.filepath)):
                    self.index_progress["processed_items"] += 1
                    continue
                pdf = PDF(item.filepath)
                pages_data = pdf.extract_text_with_pages()
                item.metadata['pages_data'] = pages_data
                text = "\n\n".join([p['text'] for p in pages_data])
                item.metadata['text'] = text if text else ""

            # Vectorize each new item
            for item in items:
                if self._cancel_indexing:
                    break
                pages_data = item.metadata.get('pages_data') or []
                if not pages_data:
                    self.index_progress["processed_items"] += 1
                    continue
                
                chunks_with_pages = self.chunk_text_with_pages(pages_data)
                if not chunks_with_pages:
                    self.index_progress["processed_items"] += 1
                    continue
                
                chunks = [c['text'] for c in chunks_with_pages]
                vectors = [get_embedding(chunk) for chunk in chunks]
                
                if vectors and len(vectors[0]) != 768:
                    print(f"WARNING: Unexpected embedding dimension {len(vectors[0])} for item {item.metadata.get('item_id')}")

                item_id = str(item.metadata.get('item_id'))
                chunk_ids = [f"{item_id}:{i}" for i in range(len(chunks))]

                meta_src = item.metadata
                title = meta_src.get("title") or ""
                authors = meta_src.get("authors") or ""
                tags = meta_src.get("tags") or ""
                collections = meta_src.get("collections") or ""
                year = meta_src.get("date") or ""
                pdf_path = meta_src.get("pdf_path") or ""

                metas = []
                for i, chunk_info in enumerate(chunks_with_pages):
                    metas.append({
                        "item_id": item_id,
                        "chunk_idx": int(i),
                        "title": title,
                        "authors": authors,
                        "tags": tags,
                        "collections": collections,
                        "year": year,
                        "pdf_path": pdf_path,
                        "page": chunk_info['page'],
                    })

                self.chroma.add_chunks(
                    ids=chunk_ids,
                    documents=chunks,
                    metadatas=metas,
                    embeddings=vectors
                )
                self.index_progress["processed_items"] += 1
                
                # Calculate time estimates
                elapsed = time.time() - self.index_progress["start_time"]
                self.index_progress["elapsed_seconds"] = int(elapsed)
                
                processed = self.index_progress["processed_items"]
                total = self.index_progress["total_items"]
                if processed > 0 and total > 0:
                    avg_time_per_item = elapsed / processed
                    remaining_items = total - processed
                    self.index_progress["eta_seconds"] = int(avg_time_per_item * remaining_items)
                
                time.sleep(0)
            
            # Rebuild BM25 index after adding new chunks
            if self.index_progress["processed_items"] > 0:
                print("Rebuilding BM25 index...")
                self.chroma.build_bm25_index()
        finally:
            self.is_indexing = False
            self._cancel_indexing = False
    
    def start_indexing(self, incremental: bool = True):
        """Start indexing in a background thread. No-op if already indexing.
        
        Args:
            incremental: If True, only index new items. If False, reindex everything.
        """
        if self.is_indexing:
            return
        self.is_indexing = True
        self._cancel_indexing = False
        # Reset progress
        self.index_progress = {
            "processed_items": 0,
            "total_items": 0,
            "start_time": None,
            "elapsed_seconds": 0,
            "eta_seconds": None,
            "skipped_items": 0,
            "mode": "incremental" if incremental else "full",
        }
        
        # Choose worker based on mode
        worker = self._index_library_incremental_worker if incremental else self._index_library_worker
        t = threading.Thread(target=worker, daemon=True)
        self._index_thread = t
        t.start()

    def cancel_indexing(self):
        """Signal cancellation for the running indexing job."""
        if not self.is_indexing:
            return
        self._cancel_indexing = True

    def chunk_text(self, text, chunk_size=800, overlap=200):
        """Improved chunking with semantic boundary awareness.
        
        Best practices for academic documents:
        - Larger chunks (600-1000 tokens) preserve context better for research papers
        - Higher overlap (150-250 tokens) ensures key concepts aren't split
        - Try to break at sentence boundaries when possible
        """
        if not text:
            return []
        
        # Split into sentences first (naive approach)
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence keeps us under chunk_size, add it
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                # Save current chunk if it's not empty
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Start new chunk
                # Include overlap from previous chunk
                if chunks and overlap > 0:
                    prev_words = current_chunk.split()
                    overlap_words = prev_words[-overlap//5:]  # rough word-based overlap
                    current_chunk = " ".join(overlap_words) + " " + sentence + " "
                else:
                    current_chunk = sentence + " "
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_text_with_pages(self, pages_data, chunk_size=800, overlap=200):
        """Chunk text while preserving page number information.
        
        Args:
            pages_data: List of dicts with 'page_num' and 'text' keys
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of dicts with 'text' and 'page' keys
        """
        import re
        
        chunks_with_pages = []
        
        for page_data in pages_data:
            page_num = page_data['page_num']
            text = page_data['text']
            
            if not text.strip():
                continue
            
            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= chunk_size:
                    current_chunk += sentence + " "
                else:
                    # Save current chunk
                    if current_chunk.strip():
                        chunks_with_pages.append({
                            'text': current_chunk.strip(),
                            'page': page_num
                        })
                    
                    # Start new chunk with overlap
                    if overlap > 0 and current_chunk:
                        prev_words = current_chunk.split()
                        overlap_words = prev_words[-overlap//5:]
                        current_chunk = " ".join(overlap_words) + " " + sentence + " "
                    else:
                        current_chunk = sentence + " "
            
            # Add final chunk from this page
            if current_chunk.strip():
                chunks_with_pages.append({
                    'text': current_chunk.strip(),
                    'page': page_num
                })
        
        return chunks_with_pages

    def build_search_prompt(self, user_query: str) -> str:
        """Build an enhanced search query using query expansion.
        
        Best practice: Transform natural questions into search-optimized queries
        that better match academic content.
        """
        base = user_query.strip()
        # Keep the original query for semantic matching
        # The embedding model will handle the expansion naturally
        return base

    def build_answer_prompt(self, question: str, snippets: list[dict]) -> str:
        """Build an optimized prompt for academic question answering.
        
        Best practices for academic RAG:
        - Clear role and constraints
        - Explicit citation requirements
        - Structured output format
        - Encourage critical analysis
        - Handle uncertainty appropriately
        """
        if not snippets:
            return (
                "You are an academic research assistant. The user asked the following question, "
                "but no relevant passages were found in their Zotero library.\n\n"
                f"Question: {question}\n\n"
                "Respond politely that you cannot find relevant information in their library for this question. "
                "Suggest they may need to: (1) add relevant papers to their library, or (2) rephrase the question "
                "to better match their existing papers."
            )

        # Build rich context with metadata
        context_blocks = []
        for s in snippets:
            cid = s["citation_id"]
            title = s.get("title", "Untitled")
            year = s.get("year", "")
            authors = s.get("authors", "Unknown")  # Get authors if available
            txt = s.get("snippet", "")
            
            # Include bibliographic context
            bib = f"{authors} ({year})" if year else authors
            context_blocks.append(f"[{cid}] {title}\n{bib}\n{txt}")

        context = "\n\n".join(context_blocks)
        
        return (
            "You are an expert research assistant helping an academic researcher understand their literature.\n\n"
            "TASK: Answer the question below using ONLY the provided excerpts from the researcher's library. "
            "Synthesize information across sources when possible.\n\n"
            "RESPONSE FORMAT:\n"
            "1. Start with a direct answer (2-3 sentences) that addresses the core question\n"
            "2. Follow with 3-5 bullet points elaborating on key details, evidence, or perspectives\n"
            "3. If sources disagree, acknowledge different viewpoints\n"
            "4. End with a brief note on limitations or gaps if relevant\n\n"
            "FORMATTING RULES:\n"
            "- When using bold text (with **), ALWAYS start it on a new line\n"
            "- Example: End a sentence with a period.\n\n**Bold Section Title**\n"
            "- Do NOT write: text continues **Bold Title** on same line\n\n"
            "CITATION RULES:\n"
            "- ALWAYS cite sources using [1], [2], etc. after every factual claim\n"
            "- Use multiple citations [1][2] when several sources support the same point\n"
            "- Never make claims without supporting citations from the context\n"
            "- If the context doesn't fully answer the question, explicitly state what's missing\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "- Do NOT use outside knowledge - only cite what's in the context\n"
            "- Do NOT speculate or extrapolate beyond what sources explicitly state\n"
            "- If sources are insufficient, say so clearly\n\n"
            "---\n\n"
            f"QUESTION: {question}\n\n"
            f"CONTEXT FROM LIBRARY:\n\n{context}\n\n"
            "---\n\n"
            "ANSWER:"
        )




    def chat(self, query, filter_item_ids=None):
        # 1) Retrieve relevant chunks using HYBRID search (dense + sparse)
        # Best practice from Reddit: Combine semantic and keyword matching
        # Retrieve more candidates (k=15-20), then re-rank and use top 6-8
        db_filter = {"item_id": {"$in": filter_item_ids}} if filter_item_ids else None
        search_prompt = self.build_search_prompt(query)
        
        # Use hybrid search combining dense embeddings + BM25
        results = self.chroma.query_hybrid(query=search_prompt, k=15, where=db_filter) or {}

        docs_outer = results.get("documents", [[]])
        metas_outer = results.get("metadatas", [[]])

        # Chroma: documents/metadatas are nested lists -> take first inner list
        docs = docs_outer[0] if docs_outer else []
        metas = metas_outer[0] if metas_outer else []
        
        # 2) RE-RANK using cross-encoder for better relevance
        # This is the key improvement from the Reddit thread
        if docs:
            ranked = rerank_passages(query, docs, top_k=10)
            # Reorder docs and metas based on re-ranking scores
            docs = [docs[idx] for idx, score in ranked]
            metas = [metas[idx] for idx, score in ranked]

        # 3) Build snippets and citation map with page numbers
        # Best practice: Prioritize diversity - limit snippets per paper
        snippets = []
        citation_map = OrderedDict()
        paper_snippet_count = {}  # Track snippets per paper
        max_snippets_per_paper = 3

        for doc, meta in zip(docs, metas):
            # meta is a dict here
            title = meta.get("title") or "Untitled"
            year = meta.get("year") or ""
            authors = meta.get("authors") or ""
            pdf_path = meta.get("pdf_path") or ""
            page = meta.get("page")  # Now we have page numbers!
            key = (title, year, pdf_path)

            # Limit snippets per paper for diversity
            paper_id = f"{title}_{year}"
            if paper_snippet_count.get(paper_id, 0) >= max_snippets_per_paper:
                continue
            
            paper_snippet_count[paper_id] = paper_snippet_count.get(paper_id, 0) + 1

            if key not in citation_map:
                citation_map[key] = len(citation_map) + 1  # 1-based index

            cid = citation_map[key]
            # Keep full chunk for academic context (don't truncate too much)
            snippet_text = (doc or "")[:800]
            snippets.append({
                "citation_id": cid,
                "snippet": snippet_text,
                "title": title,
                "year": year,
                "authors": authors,
                "pdf_path": pdf_path,
                "page": page,  # Include page number
            })
            
            # Limit total snippets for context window
            if len(snippets) >= 6:
                break

        # Build citations list with authors - need to get from snippets
        citation_to_authors = {}
        for s in snippets:
            key = (s["title"], s["year"], s["pdf_path"])
            if key not in citation_to_authors:
                citation_to_authors[key] = s["authors"]
        
        citations = [
            {
                "id": cid,
                "title": title,
                "year": year,
                "authors": citation_to_authors.get((title, year, pdf_path), ""),
                "pdf_path": pdf_path,
            }
            for (title, year, pdf_path), cid in citation_map.items()
        ]

        # 4) Call Ollama to synthesize a nice answer
        prompt = self.build_answer_prompt(query, snippets)
        try:
            summary = generate_answer(prompt)
        except Exception:
            if snippets:
                summary = snippets[0]["snippet"]
            else:
                summary = "No relevant passages found in your Zotero library."

        return {
            "summary": summary,
            "citations": citations,
            "snippets": snippets,
        }



