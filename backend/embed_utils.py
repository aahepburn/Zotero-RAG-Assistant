# embed_utils.py

from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
import os
from typing import Optional
from pathlib import Path

# Set persistent cache directory for sentence-transformers models
# This prevents re-downloading models on every startup
MODELS_CACHE_DIR = os.path.expanduser("~/.cache/sentence_transformers")
Path(MODELS_CACHE_DIR).mkdir(parents=True, exist_ok=True)
os.environ['SENTENCE_TRANSFORMERS_HOME'] = MODELS_CACHE_DIR

# Available embedding models with different speed/quality tradeoffs
EMBEDDING_MODELS = {
    'bge-base': {
        'name': 'BAAI/bge-base-en-v1.5',
        'dimension': 768,
        'description': 'High quality, state-of-the-art (768 dim, ~400MB)',
        'speed': 'medium',
        'quality': 'excellent'
    },
    'specter': {
        'name': 'allenai/specter',
        'dimension': 768,
        'description': 'Optimized for scientific documents (768 dim, ~440MB)',
        'speed': 'medium',
        'quality': 'excellent-scientific'
    },
    'minilm-l6': {
        'name': 'all-MiniLM-L6-v2',
        'dimension': 384,
        'description': 'Balanced quality and speed (384 dim, ~90MB)',
        'speed': 'fast',
        'quality': 'good'
    },
    'minilm-l3': {
        'name': 'paraphrase-MiniLM-L3-v2',
        'dimension': 384,
        'description': 'Fastest, lowest memory (384 dim, ~60MB)',
        'speed': 'fastest',
        'quality': 'moderate'
    }
}

# Default model configuration
DEFAULT_MODEL_ID = 'bge-base'
_current_model_id = DEFAULT_MODEL_ID
_current_model: Optional[SentenceTransformer] = None

def get_model_config(model_id: str = None) -> dict:
    """Get configuration for a specific embedding model."""
    mid = model_id or _current_model_id
    if mid not in EMBEDDING_MODELS:
        raise ValueError(f"Unknown embedding model: {mid}. Available: {list(EMBEDDING_MODELS.keys())}")
    return EMBEDDING_MODELS[mid]

def get_current_model_id() -> str:
    """Get the currently active model ID."""
    return _current_model_id

def get_embedding_dimension(model_id: str = None) -> int:
    """Get the embedding dimension for a specific model."""
    return get_model_config(model_id)['dimension']

def load_embedding_model(model_id: str = None) -> SentenceTransformer:
    """Load the embedding model, reusing cached instance if same model."""
    global _current_model, _current_model_id
    
    target_model_id = model_id or DEFAULT_MODEL_ID
    
    # Return cached model if already loaded and same
    if _current_model is not None and _current_model_id == target_model_id:
        return _current_model
    
    # Load new model with explicit cache directory
    config = get_model_config(target_model_id)
    print(f"Loading embedding model: {config['name']} ({config['description']})")
    _current_model = SentenceTransformer(config['name'], cache_folder=MODELS_CACHE_DIR)
    _current_model_id = target_model_id
    
    return _current_model

# Cross-encoder for re-ranking retrieved passages
# This is much more accurate than cosine similarity for relevance scoring
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', cache_folder=MODELS_CACHE_DIR)

def get_embedding(text: str, model_id: str = None) -> np.ndarray:
    """Generate embeddings for semantic search.
    
    Args:
        text: Text to embed
        model_id: Optional model ID to use (defaults to current model)
    
    Returns:
        numpy.ndarray: Embedding vector (dimension depends on model)
    """
    model = load_embedding_model(model_id)
    config = get_model_config(model_id)
    
    # Truncate very long texts to avoid memory issues
    max_length = 512  # Standard max token length
    if len(text) > max_length * 4:  # rough char estimate
        text = text[:max_length * 4]
    
    embedding = model.encode([text])[0]
    
    # Validate dimension to catch configuration issues early
    expected_dim = config['dimension']
    if len(embedding) != expected_dim:
        raise ValueError(
            f"Embedding dimension mismatch! Expected {expected_dim}, got {len(embedding)}. "
            f"Model: {config['name']}"
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
