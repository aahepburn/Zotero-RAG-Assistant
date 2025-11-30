# embed_utils.py

from sentence_transformers import SentenceTransformer

# Current model: all-MiniLM-L6-v2 (fast, 384 dimensions)
# For better academic performance, consider:
# - 'allenai/specter' or 'allenai/specter2' - purpose-built for scientific papers
# - 'sentence-transformers/all-mpnet-base-v2' - better general performance (768 dim)
# - 'BAAI/bge-large-en-v1.5' - state-of-the-art general embedding (1024 dim)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """Generate embeddings for semantic search.
    
    Best practice: For academic papers, consider using domain-specific models
    like SPECTER which are trained on citation graphs and scientific text.
    """
    return model.encode([text])[0]
