# embed_utils.py

from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# UPGRADED: Using BGE-base for better retrieval (768 dimensions)
# BGE is state-of-the-art for general retrieval and works well for academic papers
# Using base version for faster loading (~400MB vs 1.3GB for large)
# Still significantly better than all-MiniLM-L6-v2 for academic content
MODEL_NAME = 'BAAI/bge-base-en-v1.5'
EMBEDDING_DIMENSION = 768  # BGE-base produces 768-dimensional embeddings

model = SentenceTransformer(MODEL_NAME)

# Cross-encoder for re-ranking retrieved passages
# This is much more accurate than cosine similarity for relevance scoring
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def get_embedding(text):
    """Generate embeddings for semantic search using BGE-base.
    
    BGE (BAAI General Embedding) is state-of-the-art for retrieval tasks
    and provides excellent performance on academic content.
    
    Important: BGE models work best with the query prefix for queries,
    but for document chunks we use them as-is.
    
    Returns:
        numpy.ndarray: 768-dimensional embedding vector
    """
    # Truncate very long texts to avoid memory issues
    max_length = 512  # BGE max token length
    if len(text) > max_length * 4:  # rough char estimate
        text = text[:max_length * 4]
    embedding = model.encode([text])[0]
    
    # Validate dimension to catch configuration issues early
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Embedding dimension mismatch! Expected {EMBEDDING_DIMENSION}, got {len(embedding)}. "
            f"Model: {MODEL_NAME}"
        )
    
    return embedding

def rerank_passages(query: str, passages: list[str], top_k: int = None) -> list[tuple[int, float]]:
    """Re-rank passages using cross-encoder for better relevance scoring.
    
    Args:
        query: The user's query
        passages: List of text passages to rank
        top_k: Optional limit on number of results to return
    
    Returns:
        List of (index, score) tuples sorted by relevance score (descending)
    """
    if not passages:
        return []
    
    # Create query-passage pairs for the cross-encoder
    pairs = [[query, passage] for passage in passages]
    
    # Get relevance scores
    scores = reranker.predict(pairs)
    
    # Sort by score (descending) and return indices with scores
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    
    if top_k:
        ranked = ranked[:top_k]
    
    return ranked
