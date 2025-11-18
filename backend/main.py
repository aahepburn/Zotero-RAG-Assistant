from fastapi import FastAPI, Query
from typing import Optional
from backend.pdf_utils import extract_text

# If you add semantic search (optional for now):
from backend.index_utils import collection, get_embedding


app = FastAPI()

@app.get("/")
def read_root():
    """
    Health check endpoint for Zotero LLM backend.
    """
    return {"msg": "Welcome to Zotero LLM Plugin backend"}

@app.get("/pdfsample")
def pdf_sample(
    filename: str = Query(..., description="Path to PDF file, e.g. backend/sample_pdfs/test_article.pdf"),
    max_chars: Optional[int] = Query(2000, description="Maximum number of characters to extract"),
):
    """
    Extracts sample text from a PDF for testing purposes.
    Returns a JSON object with extracted text or error message.
    """
    try:
        text = extract_text(filename, max_chars)
        return {"sample": text}
    except Exception as e:
        return {"error": str(e)}

# Uncomment when index_utils.py and embedding/search are ready:
@app.get("/search")
def search(query: str, top_k: int = 3):
    """
    Semantic search across embedded documents.
    Returns top-k matches with their text and filenames.
    """
    try:
        embedding = get_embedding(query)
        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return {
            "results": [
                {"text": doc, "filename": meta["filename"]}
                for doc, meta in zip(results["documents"][0], results["metadatas"][0])
            ]
        }
    except Exception as e:
        return {"error": str(e)}
