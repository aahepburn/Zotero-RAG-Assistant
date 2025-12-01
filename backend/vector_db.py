#vector_db.py
import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any, Iterable, Optional
from rank_bm25 import BM25Okapi
import pickle
import numpy as np

class ChromaClient:
    """
    Administers user interactions with the Chroma vector database for Zotero library items.
    Supports persistent per-library DB, bulk chunk addition, semantic querying, and sync with Zotero snapshot.
    
    IMPORTANT: This class expects pre-computed embeddings and does NOT use ChromaDB's 
    default embedding function. All embeddings must be generated using get_embedding() 
    from embed_utils.py to ensure consistent dimensional vectors.
    
    Each embedding model gets its own collection to prevent dimension mismatch errors.
    """

    def __init__(self, db_path: str, collection_name: str = "zotero_lib", embedding_model_id: str = "bge-base"):
        self.db_path = db_path
        self.embedding_model_id = embedding_model_id
        # Include embedding model in collection name to avoid dimension conflicts
        self.collection_name = f"{collection_name}_{embedding_model_id}"
        os.makedirs(self.db_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=self.db_path, settings=Settings())
        
        # Create collection WITHOUT an embedding function (we provide embeddings manually)
        # This prevents ChromaDB from using its default all-MiniLM-L6-v2 (384 dims)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "hnsw:space": "cosine",  # Use cosine similarity for retrieval
                "embedding_model": embedding_model_id  # Track which model created this collection
            }
        )
        
        # BM25 index for sparse retrieval (loaded lazily)
        # Each embedding model has its own BM25 index
        self.bm25_index = None
        self.bm25_corpus = None
        self.bm25_ids = None
        self.bm25_path = os.path.join(self.db_path, f"bm25_index_{embedding_model_id}.pkl")

    def add_chunks(self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """
        Bulk-adds document chunks and their vectors to the Chroma collection.
        """
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query_db(self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the vector DB with a natural-language question.
        Optionally filter by metadata keys (e.g. item_id).
        
        CRITICAL: Manually embeds the query using get_embedding() to ensure
        consistent 768-dimensional embeddings. DO NOT use query_texts parameter
        as it would trigger ChromaDB's default embedding function.
        """
        from backend.embed_utils import get_embedding
        
        # Manually embed query to ensure consistent dimensions
        query_embedding = get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],  # Use query_embeddings, not query_texts!
            n_results=k,
            where=where,
        )
        return results
    
    def query_bm25(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Query using BM25 sparse retrieval.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of dicts with 'id', 'score', 'document', and 'metadata'
        """
        if self.bm25_index is None:
            self._load_bm25_index()
        
        if self.bm25_index is None:
            return []  # No BM25 index available
        
        # Tokenize query (simple whitespace tokenization)
        query_tokens = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top k indices
        top_indices = np.argsort(scores)[::-1][:k]
        
        # Retrieve documents from ChromaDB
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                doc_id = self.bm25_ids[idx]
                # Get full document and metadata from ChromaDB
                chroma_result = self.collection.get(ids=[doc_id])
                if chroma_result['ids']:
                    results.append({
                        'id': doc_id,
                        'score': float(scores[idx]),
                        'document': chroma_result['documents'][0],
                        'metadata': chroma_result['metadatas'][0]
                    })
        
        return results
    
    def query_hybrid(self, query: str, k: int = 10, where: Optional[Dict[str, Any]] = None, embedding_model_id: str = "bge-base") -> Dict[str, Any]:
        """Hybrid search combining dense (semantic) and sparse (BM25) retrieval.
        
        Best practice from Reddit thread: Retrieve top-k from both methods,
        create a union, then re-rank using cross-encoder.
        
        Args:
            query: Search query
            k: Number of results from each method
            where: Optional metadata filter
            embedding_model_id: ID of the embedding model to use (default: "bge-base")
            
        Returns:
            Combined results dict with documents, metadatas, and distances
        """
        from backend.embed_utils import get_embedding
        
        # Embed query using the configured embedding model
        query_embedding = get_embedding(query, model_id=embedding_model_id)
        
        # Get dense retrieval results
        dense_results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],  # Use query_embeddings, not query_texts!
            n_results=k,
            where=where,
        )
        
        # Get sparse retrieval results
        bm25_results = self.query_bm25(query, k=k)
        
        # Combine results (union of document IDs)
        seen_ids = set()
        combined_docs = []
        combined_metas = []
        combined_ids = []
        
        # Add dense results
        if dense_results['ids'] and dense_results['ids'][0]:
            for i, doc_id in enumerate(dense_results['ids'][0]):
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    combined_ids.append(doc_id)
                    combined_docs.append(dense_results['documents'][0][i])
                    combined_metas.append(dense_results['metadatas'][0][i])
        
        # Add BM25 results not already included
        for result in bm25_results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                combined_ids.append(result['id'])
                combined_docs.append(result['document'])
                combined_metas.append(result['metadata'])
        
        # Format as ChromaDB-style result
        return {
            'ids': [combined_ids],
            'documents': [combined_docs],
            'metadatas': [combined_metas],
            'distances': [[0.0] * len(combined_ids)]  # Placeholder, will be re-ranked
        }
    
    def _load_bm25_index(self):
        """Load BM25 index from disk if it exists."""
        if os.path.exists(self.bm25_path):
            try:
                with open(self.bm25_path, 'rb') as f:
                    data = pickle.load(f)
                    self.bm25_index = data['index']
                    self.bm25_corpus = data['corpus']
                    self.bm25_ids = data['ids']
            except Exception as e:
                print(f"Error loading BM25 index: {e}")
                self.bm25_index = None
    
    def _save_bm25_index(self):
        """Save BM25 index to disk."""
        if self.bm25_index is not None:
            try:
                with open(self.bm25_path, 'wb') as f:
                    pickle.dump({
                        'index': self.bm25_index,
                        'corpus': self.bm25_corpus,
                        'ids': self.bm25_ids
                    }, f)
            except Exception as e:
                print(f"Error saving BM25 index: {e}")
    
    def build_bm25_index(self):
        """Build BM25 index from all documents in ChromaDB."""
        # Get all documents from ChromaDB
        all_docs = self.collection.get()
        
        if not all_docs['ids']:
            print("No documents in collection to index")
            return
        
        # Tokenize documents (simple whitespace tokenization)
        corpus = []
        for doc in all_docs['documents']:
            tokens = doc.lower().split()
            corpus.append(tokens)
        
        # Build BM25 index
        self.bm25_corpus = corpus
        self.bm25_ids = all_docs['ids']
        self.bm25_index = BM25Okapi(corpus)
        
        # Save index
        self._save_bm25_index()
        print(f"BM25 index built with {len(corpus)} documents")

    def sync_db(self,
        items: Iterable[Any],  
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embed_fn=None,
    ) -> None:
        """
        Syncs the Chroma DB with the current ZoteroItem snapshot.
        Indexes and chunks text, embeds with supplied function, and stores metadata.
        """

        def chunk_text(t: str, size: int, overlap: int) -> List[str]:
            chunks = []
            start = 0
            n = len(t)
            while start < n:
                end = min(n, start + size)
                chunks.append(t[start:end])
                if end == n:
                    break
                start = end - overlap
            return chunks

        ids: List[str] = []
        docs: List[str] = []
        metas: List[Dict[str, Any]] = []
        embeddings: List[List[float]] = []

        for item in items:
            text = getattr(item, "metadata", {}).get("text") or item.get("text") if isinstance(item, dict) else None
            item_id = getattr(item, "metadata", {}).get("item_id") or item.get("item_id") if isinstance(item, dict) else None
            if not text or not item_id:
                continue
            chunks = chunk_text(text, chunk_size, chunk_overlap)
            meta_src = getattr(item, "metadata", {}) if hasattr(item, "metadata") else item
            ids_batch = []
            docs_batch = []
            metas_batch = []
            for idx, ch in enumerate(chunks):
                doc_id = f"{str(item_id)}:{str(idx)}"
                ids_batch.append(doc_id)
                docs_batch.append(ch)

                title = meta_src.get("title") or ""
                authors = meta_src.get("authors") or ""
                tags = meta_src.get("tags") or ""
                collections = meta_src.get("collections") or ""
                year = meta_src.get("date") or ""
                pdf_path = meta_src.get("pdf_path") or ""

                metas_batch.append({
                    "item_id": str(item_id),
                    "chunk_idx": int(idx),
                    "title": title,
                    "authors": authors,
                    "tags": tags,
                    "collections": collections,
                    "year": year,
                    "pdf_path": pdf_path,
                })
            ids += ids_batch
            docs += docs_batch
            metas += metas_batch
            # ----- Embed batch -----
            if embed_fn is not None and docs_batch:
                embeddings += self.embed_chunks(docs_batch, embed_fn)
        if ids:
            print("ID types:", set(type(i) for i in ids))
            self.add_chunks(
                ids=[str(i) for i in ids],
                documents=docs,
                metadatas=metas,
                embeddings=embeddings if embed_fn is not None else None
            )

    def get_or_create_db(self):
        """
        Ensures the collection exists and is initialized.
        IMPORTANT: Creates collection without embedding function (manual embeddings only).
        """
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_indexed_item_ids(self) -> set:
        """
        Get all unique item IDs that are currently indexed in the database.
        
        Returns:
            Set of item_id strings
        """
        # Get all documents with their metadata
        all_data = self.collection.get()
        
        if not all_data['metadatas']:
            return set()
        
        # Extract unique item_ids from metadata
        item_ids = set()
        for metadata in all_data['metadatas']:
            if metadata and 'item_id' in metadata:
                item_ids.add(metadata['item_id'])
        
        return item_ids
    
    def item_exists(self, item_id: str) -> bool:
        """
        Check if an item is already indexed in the database.
        
        Args:
            item_id: The Zotero item ID to check
            
        Returns:
            True if item exists, False otherwise
        """
        # Query for any chunk with this item_id
        results = self.collection.get(
            where={"item_id": str(item_id)},
            limit=1
        )
        return len(results['ids']) > 0
    
    def get_item_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an indexed item.
        
        Args:
            item_id: The Zotero item ID
            
        Returns:
            Metadata dict or None if not found
        """
        results = self.collection.get(
            where={"item_id": str(item_id)},
            limit=1
        )
        
        if results['metadatas']:
            return results['metadatas'][0]
        return None
    
    def delete_item(self, item_id: str) -> int:
        """
        Delete all chunks associated with an item from the database.
        
        Args:
            item_id: The Zotero item ID to delete
            
        Returns:
            Number of chunks deleted
        """
        # Get all chunk IDs for this item
        results = self.collection.get(
            where={"item_id": str(item_id)}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        return 0

    def embed_chunks(self, chunks: List[str], embed_fn) -> List[List[float]]:
        """
        Passes a list of text chunks through the embedding function and returns their vectors.
        """
        embeddings = [embed_fn(chunk) for chunk in chunks]
        return embeddings
    
    def get_document_count(self) -> int:
        """
        Get total number of document chunks in the collection.
        
        Returns:
            Number of chunks indexed
        """
        return self.collection.count()
    
    def validate_embedding_dimension(self) -> Dict[str, Any]:
        """
        Validate that the database is configured correctly for the current embedding model.
        
        Returns:
            Dict with validation results including expected vs actual dimensions
        """
        from backend.embed_utils import EMBEDDING_DIMENSION, MODEL_NAME, get_embedding
        
        # Try to get a sample document to check dimensions
        sample = self.collection.get(limit=1)
        
        if not sample['ids']:
            return {
                "status": "empty",
                "message": "Database is empty. Re-indexing required.",
                "expected_dimension": EMBEDDING_DIMENSION,
                "model": MODEL_NAME
            }
        
        # Test embedding a simple query
        test_embedding = get_embedding("test query")
        
        return {
            "status": "ok",
            "message": "Database configuration is valid",
            "expected_dimension": EMBEDDING_DIMENSION,
            "actual_dimension": len(test_embedding),
            "model": MODEL_NAME,
            "document_count": len(sample['ids'])
        }
