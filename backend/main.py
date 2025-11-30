# backend/main.py
# uvicorn backend.main:app --reload
from fastapi import FastAPI, Query, Body
from typing import Optional
from backend.zoteroitem import ZoteroItem
from backend.external_api_utils import fetch_google_book_reviews, fetch_semantic_scholar_data
from backend.pdf import PDF
from backend.zotero_dbase import ZoteroLibrary
from fastapi.middleware.cors import CORSMiddleware
from backend.interface import ZoteroChatbot
from backend.embed_utils import get_embedding
import os
import json
from pathlib import Path

app = FastAPI()

# Settings file path
SETTINGS_DIR = Path.home() / ".zotero-llm"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

# Ensure settings directory exists
SETTINGS_DIR.mkdir(parents=True, exist_ok=True) 

# CORS setup: matches your frontend HTML server (e.g., http://localhost:8080)
app.add_middleware(
    CORSMiddleware,
    # Allow the typical dev server origins (Vite default 5173 and older 8080),
    # plus localhost variants used during development.
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/Users/aahepburn/Zotero/zotero.sqlite"
CHROMA_PATH = "/Users/aahepburn/.zotero-llm/chroma/user-1"

# Instantiate the main chatbot object
chatbot = ZoteroChatbot(DB_PATH, CHROMA_PATH)

@app.get("/")
def read_root():
    """Health check endpoint for Zotero LLM backend."""
    return {"msg": "Welcome to Zotero LLM Plugin backend"}

@app.get("/pdfsample")
def pdf_sample(
    filename: str = Query(..., description="Path to PDF file, e.g. backend/sample_pdfs/test_article.pdf"),
    max_chars: Optional[int] = Query(2000, description="Maximum number of characters to extract"),
):
    """Extracts sample text from a PDF for testing purposes."""
    try:
        pdf = PDF(filepath=filename)
        text = pdf.extract_text(max_chars=max_chars)
        return {"sample": text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/item_metadata")
def get_item_metadata(
    filename: str = Query(..., description="Path to PDF or metadata file"),
):
    """Retrieves metadata from the ZoteroItem class."""
    try:
        item = ZoteroItem(filepath=filename)
        title = item.get_title()
        author = item.get_author()
        return {"title": title, 
                "author": author}
    except Exception as e:
        return {"error": str(e)}

@app.get("/search_items")
def search_items(
    authors: Optional[str] = Query("", description="Comma separated authors"),
    titles: Optional[str] = Query("", description="Comma separated titles"),
    dates: Optional[str] = Query("", description="Comma separated dates")
):
    """Query the Zotero library using authors, titles, and dates."""
    try:
        authors_list = [a.strip() for a in authors.split(",") if a.strip()]
        titles_list = [t.strip() for t in titles.split(",") if t.strip()]
        dates_list = [d.strip() for d in dates.split(",") if d.strip()]
        # Fix SQLite threading issue: check_same_thread=False inside ZoteroLibrary class!
        zlib = ZoteroLibrary(DB_PATH)
        results = zlib.search_parent_items(authors=authors_list, titles=titles_list, dates=dates_list)
        return {"results": list(results)}  # Convert set to list for JSON serialization
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_gbook_reviews")
def get_reviews(query: str):
    """Makes a call to the Google Books API to retrieve reviews."""
    try:
        reviews = fetch_google_book_reviews(query)
        return {"reviews": reviews}
    except Exception as e:
        return {"error": str(e)}

@app.post("/index_library")
def index_library(payload: dict = Body(default={"incremental": True})):
    """Index Zotero parent items and PDFs in the vector database.
    
    Args:
        payload: JSON with optional "incremental" boolean (default: True)
                 - True: Only index new items not already in the database
                 - False: Full reindex of all items
    """
    try:
        incremental = payload.get("incremental", True)
        chatbot.start_indexing(incremental=incremental)
        mode = "incremental" if incremental else "full"
        return {"msg": f"Indexing started ({mode} mode)."}
    except Exception as e:
        return {"error": str(e)}


@app.post("/index_cancel")
def index_cancel():
    """Cancel a running indexing job."""
    try:
        chatbot.cancel_indexing()
        return {"msg": "Cancellation signaled."}
    except Exception as e:
        return {"error": str(e)}

import traceback

@app.get("/chat")
def chat(query: str, item_ids: Optional[str] = Query("", description="Comma separated Zotero item IDs to scope search")):
    try:
        filter_ids = [id_.strip() for id_ in item_ids.split(",") if id_.strip()]
        payload = chatbot.chat(query, filter_item_ids=filter_ids if filter_ids else None)
        return payload
    except Exception as e:
        tb = traceback.format_exc()
        return {"error": str(e), "traceback": tb}


@app.post("/chat")
def chat_post(payload: dict = Body(...)):
    """POST-style chat endpoint that accepts JSON body: {"query": "...", "item_ids": ["id1","id2"]}
    This mirrors the GET `/chat` endpoint but is easier for clients that send JSON.
    """
    try:
        query = payload.get("query")
        if not query:
            return {"error": "Missing 'query' in request body"}

        item_ids = payload.get("item_ids") or []
        # Accept either a list of ids or a comma-separated string
        if isinstance(item_ids, str):
            filter_ids = [id_.strip() for id_ in item_ids.split(",") if id_.strip()]
        elif isinstance(item_ids, list):
            filter_ids = [str(id_).strip() for id_ in item_ids if str(id_).strip()]
        else:
            filter_ids = []

        payload_out = chatbot.chat(query, filter_item_ids=filter_ids if filter_ids else None)
        return payload_out
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages for common issues
        if "embedding with dimension" in error_msg.lower():
            return {
                "error": "Database configuration error: Embedding dimension mismatch detected. "
                        "This usually means your database was created with a different embedding model. "
                        "Please delete the vector database and re-index your library. "
                        "Run: rm -rf " + CHROMA_PATH + " then use the Index Library button.",
                "technical_details": error_msg,
                "traceback": traceback.format_exc()
            }
        
        tb = traceback.format_exc()
        return {"error": error_msg, "traceback": tb}


@app.get("/index_status")
def index_status():
    """Return a simple status for indexing. Currently basic placeholder.
    You can expand this to report real progress/state from the ZoteroChatbot.
    """
    try:
        status = "indexing" if getattr(chatbot, "is_indexing", False) else "idle"
        progress = getattr(chatbot, "index_progress", None) or {}
        return {"status": status, "progress": progress}
    except Exception as e:
        return {"error": str(e)}


@app.get("/db_health")
def db_health():
    """Check the health and configuration of the vector database.
    Validates that embedding dimensions are consistent.
    """
    try:
        validation = chatbot.chroma.validate_embedding_dimension()
        return validation
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/index_stats")
def index_stats():
    """Get statistics about the indexed library.
    
    Returns:
        - indexed_items: Number of unique items in the database
        - total_chunks: Total number of text chunks indexed
        - zotero_items: Total number of items in Zotero library with PDFs
        - new_items: Number of items in Zotero not yet indexed
    """
    try:
        # Get indexed item IDs
        indexed_ids = chatbot.chroma.get_indexed_item_ids()
        
        # Get total chunks
        total_chunks = chatbot.chroma.get_document_count()
        
        # Get all Zotero items
        raw_items = chatbot.zlib.search_parent_items_with_pdfs()
        zotero_item_ids = {str(it['item_id']) for it in raw_items}
        
        # Calculate new items
        new_item_ids = zotero_item_ids - indexed_ids
        
        return {
            "indexed_items": len(indexed_ids),
            "total_chunks": total_chunks,
            "zotero_items": len(zotero_item_ids),
            "new_items": len(new_item_ids),
            "needs_sync": len(new_item_ids) > 0
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/open_pdf")
def open_pdf(payload: dict = Body(...)):
    """Open a PDF file with the system's default viewer.
    Expects JSON body: {"pdf_path": "/path/to/file.pdf"}
    """
    import subprocess
    import platform
    import os
    
    try:
        pdf_path = payload.get("pdf_path")
        if not pdf_path:
            return {"error": "Missing 'pdf_path' in request body"}
        
        if not os.path.exists(pdf_path):
            return {"error": f"PDF file not found: {pdf_path}"}
        
        # Open the file with the system's default application
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", pdf_path], check=True)
        elif system == "Windows":
            os.startfile(pdf_path)
        elif system == "Linux":
            subprocess.run(["xdg-open", pdf_path], check=True)
        else:
            return {"error": f"Unsupported operating system: {system}"}
        
        return {"success": True, "message": f"Opened {pdf_path}"}
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to open PDF: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/ollama_status")
def ollama_status():
    """Check if Ollama is running and responsive."""
    import requests
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            models = data.get("models", [])
            return {
                "status": "running",
                "models": [m.get("name") for m in models] if models else []
            }
        else:
            return {"status": "error", "message": "Ollama responded with error"}
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "message": "Cannot connect to Ollama"}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "message": "Ollama request timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def load_settings():
    """Load settings from JSON file."""
    default_settings = {
        "openaiApiKey": "",
        "anthropicApiKey": "",
        "defaultModel": "ollama",
        "zoteroPath": DB_PATH,
        "chromaPath": CHROMA_PATH,
    }
    
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                saved_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_settings, **saved_settings}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
    return default_settings


def save_settings(settings: dict):
    """Save settings to JSON file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


@app.get("/settings")
def get_settings():
    """Get current application settings."""
    try:
        settings = load_settings()
        # Don't send full API keys to frontend for security
        # Just indicate if they're set
        return {
            **settings,
            "openaiApiKey": "***" if settings.get("openaiApiKey") else "",
            "anthropicApiKey": "***" if settings.get("anthropicApiKey") else "",
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/settings")
def update_settings(settings: dict = Body(...)):
    """Update application settings."""
    try:
        current_settings = load_settings()
        
        # Handle API keys specially - only update if not masked
        for key in ["openaiApiKey", "anthropicApiKey"]:
            if key in settings:
                # If frontend sends "***", keep the existing key
                if settings[key] == "***":
                    settings[key] = current_settings.get(key, "")
        
        # Update settings
        updated_settings = {**current_settings, **settings}
        
        if save_settings(updated_settings):
            # Update global paths if they changed
            global DB_PATH, CHROMA_PATH
            if "zoteroPath" in settings:
                DB_PATH = settings["zoteroPath"]
            if "chromaPath" in settings:
                CHROMA_PATH = settings["chromaPath"]
            
            return {"success": True, "message": "Settings saved successfully"}
        else:
            return {"error": "Failed to save settings"}
    except Exception as e:
        return {"error": str(e)}


