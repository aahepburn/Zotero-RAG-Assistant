# interface.py

from backend.zotero_dbase import ZoteroLibrary
from backend.zoteroitem import ZoteroItem
from backend.pdf import PDF
from backend.vector_db import ChromaClient
from backend.embed_utils import get_embedding
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
        }
        self._index_thread = None
    
    def _index_library_worker(self):
        try:
            raw_items = self.zlib.search_parent_items_with_pdfs()
            self.index_progress["total_items"] = len(raw_items)
            self.index_progress["processed_items"] = 0
            items = [ZoteroItem(filepath=it['pdf_path'], metadata=it) for it in raw_items]

            # Extract text for each item using PDF logic
            for item in items:
                if self._cancel_indexing:
                    break
                if not (item.filepath and os.path.exists(item.filepath)):
                    self.index_progress["processed_items"] += 1
                    continue  # Skip missing or inaccessible PDFs
                pdf = PDF(item.filepath)
                text = pdf.extract_text()
                item.metadata['text'] = text if text else ""

            # Vectorize each item's text (chunk/embedding logic)
            for item in items:
                if self._cancel_indexing:
                    break
                text = item.metadata.get('text') or ""
                if not text:
                    self.index_progress["processed_items"] += 1
                    continue
                chunks = self.chunk_text(text)
                if not chunks:
                    self.index_progress["processed_items"] += 1
                    continue
                vectors = [get_embedding(chunk) for chunk in chunks]

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
                for i in range(len(chunks)):
                    metas.append({
                        "item_id": item_id,
                        "chunk_idx": int(i),
                        "title": title,
                        "authors": authors,
                        "tags": tags,
                        "collections": collections,
                        "year": year,
                        "pdf_path": pdf_path,
                    })

                self.chroma.add_chunks(
                    ids=chunk_ids,
                    documents=chunks,
                    metadatas=metas,
                    embeddings=vectors
                )
                # Update progress after processing this item
                self.index_progress["processed_items"] += 1
                # small sleep to allow cancellation to be checked promptly in CPU-bound loops
                time.sleep(0)
        finally:
            self.is_indexing = False
            self._cancel_indexing = False

    def start_indexing(self):
        """Start indexing in a background thread. No-op if already indexing."""
        if self.is_indexing:
            return
        self.is_indexing = True
        self._cancel_indexing = False
        # Reset progress
        self.index_progress = {"processed_items": 0, "total_items": 0}
        t = threading.Thread(target=self._index_library_worker, daemon=True)
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
        # 1) Retrieve relevant chunks from Chroma
        # Best practice: Retrieve more candidates (k=10-20) for better coverage
        # Then use top 5-8 for context window management
        db_filter = {"item_id": {"$in": filter_item_ids}} if filter_item_ids else None
        search_prompt = self.build_search_prompt(query)
        results = self.chroma.query_db(query=search_prompt, k=10, where=db_filter) or {}

        docs_outer = results.get("documents", [[]])
        metas_outer = results.get("metadatas", [[]])

        # Chroma: documents/metadatas are nested lists -> take first inner list
        docs = docs_outer[0] if docs_outer else []
        metas = metas_outer[0] if metas_outer else []

        # 2) Build snippets and citation map
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

        # 3) Call Ollama to synthesize a nice answer
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



