# backend/index_utils.py

import os
import chromadb
from backend.pdf import extract_text   # You only need this import

client = chromadb.PersistentClient(path="vector_db/")
collection = client.get_or_create_collection("library")

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Generate an embedding vector for given text using a sentence transformer model.
    """
    return model.encode([text])[0]

def index_pdf(pdf_path):
    """
    Parse a PDF, create an embedding, and add it to the vector DB.
    """
    text = extract_text(pdf_path, max_chars=5000)
    embedding = get_embedding(text)
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{"filename": pdf_path}]
    )
