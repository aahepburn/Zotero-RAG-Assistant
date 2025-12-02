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
from backend.vector_db import ChromaClient
from backend.embed_utils import get_embedding
from backend.profile_manager import ProfileManager
import os
import json
from pathlib import Path

app = FastAPI()

# Initialize profile manager
try:
    profile_manager = ProfileManager()
    print(f"ProfileManager initialized at: {profile_manager.BASE_DIR}")
    
    # Get active profile (will create default if none exists)
    active_profile = profile_manager.get_active_profile()
    if not active_profile:
        print("WARNING: No active profile found, attempting to create default...")
        active_profile = profile_manager.get_active_profile()  # Should auto-create
    
    if active_profile:
        print(f"Active profile: {active_profile['id']} - {active_profile['name']}")
    else:
        raise RuntimeError("Failed to initialize profile system")
except Exception as e:
    print(f"ERROR initializing profile system: {e}")
    import traceback
    traceback.print_exc()
    raise 

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


def load_settings(profile_id: str = None):
    """Load settings from profile storage.
    
    Args:
        profile_id: Profile ID to load settings from. If None, uses active profile.
    """
    if profile_id is None:
        active = profile_manager.get_active_profile()
        if not active:
            raise RuntimeError("No active profile")
        profile_id = active['id']
    
    default_settings = {
        "activeProviderId": "ollama",
        "activeModel": "",
        "embeddingModel": "bge-base",
        "zoteroPath": DB_PATH,
        "chromaPath": CHROMA_PATH,
        "providers": {
            "ollama": {
                "enabled": True,
                "credentials": {
                    "base_url": "http://localhost:11434"
                }
            },
            "openai": {
                "enabled": False,
                "credentials": {
                    "api_key": ""
                }
            },
            "anthropic": {
                "enabled": False,
                "credentials": {
                    "api_key": ""
                }
            },
            "perplexity": {
                "enabled": False,
                "credentials": {
                    "api_key": ""
                }
            },
            "google": {
                "enabled": False,
                "credentials": {
                    "api_key": ""
                }
            },
            "groq": {
                "enabled": False,
                "credentials": {
                    "api_key": ""
                }
            },
            "openrouter": {
                "enabled": False,
                "credentials": {
                    "api_key": ""
                }
            }
        }
    }
    
    # Load profile-specific settings
    saved_settings = profile_manager.load_profile_settings(profile_id)
    if saved_settings:
        try:
            # Migrate old settings format if needed
            if "openaiApiKey" in saved_settings or "anthropicApiKey" in saved_settings:
                    # Old format - migrate to new
                    migrated = default_settings.copy()
                    
                    if saved_settings.get("openaiApiKey"):
                        migrated["providers"]["openai"]["credentials"]["api_key"] = saved_settings["openaiApiKey"]
                        migrated["providers"]["openai"]["enabled"] = True
                    
                    if saved_settings.get("anthropicApiKey"):
                        migrated["providers"]["anthropic"]["credentials"]["api_key"] = saved_settings["anthropicApiKey"]
                        migrated["providers"]["anthropic"]["enabled"] = True
                    
                    if saved_settings.get("zoteroPath"):
                        migrated["zoteroPath"] = saved_settings["zoteroPath"]
                    
                    if saved_settings.get("chromaPath"):
                        migrated["chromaPath"] = saved_settings["chromaPath"]
                    
                    # Migrate defaultModel
                    if saved_settings.get("defaultModel"):
                        old_model = saved_settings["defaultModel"]
                        if old_model == "ollama":
                            migrated["activeProviderId"] = "ollama"
                        elif old_model.startswith("gpt"):
                            migrated["activeProviderId"] = "openai"
                            migrated["activeModel"] = old_model
                        elif old_model.startswith("claude"):
                            migrated["activeProviderId"] = "anthropic"
                            migrated["activeModel"] = old_model
                    
                    # Save migrated settings
                    save_settings(migrated, profile_id)
                    return migrated
            else:
                # New format - merge with defaults
                merged = default_settings.copy()
                merged.update(saved_settings)
                
                # Ensure all providers exist in settings
                if "providers" in saved_settings:
                    for provider_id in default_settings["providers"]:
                        if provider_id not in merged["providers"]:
                            merged["providers"][provider_id] = default_settings["providers"][provider_id]
                
                return merged
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
    else:
        return default_settings


def save_settings(settings: dict, profile_id: str = None):
    """Save settings to profile storage.
    
    Args:
        settings: Settings dictionary
        profile_id: Profile ID to save to. If None, uses active profile.
    """
    if profile_id is None:
        active = profile_manager.get_active_profile()
        if not active:
            return False
        profile_id = active['id']
    
    return profile_manager.save_profile_settings(profile_id, settings)


# Instantiate the main chatbot object with provider settings
def initialize_chatbot():
    """Initialize chatbot with current profile settings."""
    active = profile_manager.get_active_profile()
    if not active:
        raise RuntimeError("No active profile")
    
    settings = load_settings(active['id'])
    
    # Extract provider credentials
    provider_credentials = {}
    for provider_id, provider_config in settings.get("providers", {}).items():
        if provider_config.get("enabled"):
            provider_credentials[provider_id] = provider_config.get("credentials", {})
    
    # Use profile-specific chroma path if not customized
    chroma_path = settings.get("chromaPath")
    if not chroma_path:
        chroma_path = profile_manager.get_profile_chroma_path(active['id'])
    
    return ZoteroChatbot(
        db_path=settings.get("zoteroPath", DB_PATH),
        chroma_path=chroma_path,
        active_provider_id=settings.get("activeProviderId", "ollama"),
        active_model=settings.get("activeModel"),
        credentials=provider_credentials,
        embedding_model_id=settings.get("embeddingModel", "bge-base")
    )

chatbot = initialize_chatbot()

@app.get("/")
def read_root():
    """Health check endpoint for Zotero LLM backend."""
    return {"msg": "Welcome to Zotero LLM Plugin backend"}

@app.head("/")
def read_root_head():
    """Health check endpoint (HEAD) for Zotero LLM backend."""
    return {"msg": "Welcome to Zotero LLM Plugin backend"}

@app.get("/health")
def health_check():
    """
    Detailed health check endpoint that validates all critical components.
    Returns structured health information for diagnostics.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "components": {}
        }
        
        # Check profile system
        try:
            active = profile_manager.get_active_profile()
            health_status["components"]["profile_manager"] = {
                "status": "ok",
                "active_profile": active["id"] if active else None
            }
        except Exception as e:
            health_status["components"]["profile_manager"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check database path
        try:
            db_exists = os.path.exists(DB_PATH)
            health_status["components"]["database"] = {
                "status": "ok" if db_exists else "warning",
                "path": DB_PATH,
                "exists": db_exists
            }
            if not db_exists:
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }

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
    """POST-style chat endpoint that accepts JSON body: {"query": "...", "item_ids": ["id1","id2"], "session_id": "..."}
    This mirrors the GET `/chat` endpoint but is easier for clients that send JSON.
    Supports stateful conversations via session_id.
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

        # Extract session_id for stateful conversation
        session_id = payload.get("session_id")

        payload_out = chatbot.chat(
            query, 
            filter_item_ids=filter_ids if filter_ids else None,
            session_id=session_id
        )
        print(f"Endpoint returning payload_out with generated_title: {payload_out.get('generated_title')}")
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
            "needs_sync": len(new_item_ids) > 0,
            "current_embedding_model": chatbot.embedding_model_id,
            "collection_name": chatbot.chroma.collection_name
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/embedding_collections")
def list_embedding_collections():
    """List all available embedding model collections in the database.
    Shows which embedding models have been used to index the library.
    """
    try:
        settings = load_settings()
        chroma_path = settings.get("chromaPath", CHROMA_PATH)
        
        # Create a temporary ChromaDB client to list collections
        import chromadb
        from chromadb.config import Settings
        client = chromadb.PersistentClient(path=chroma_path, settings=Settings())
        
        collections = client.list_collections()
        
        # Parse collection names to extract embedding models
        embedding_collections = []
        for col in collections:
            # Collection names follow pattern: zotero_lib_{embedding_model_id}
            if col.name.startswith("zotero_lib_"):
                embedding_model_id = col.name.replace("zotero_lib_", "")
                item_count = col.count()
                embedding_collections.append({
                    "collection_name": col.name,
                    "embedding_model_id": embedding_model_id,
                    "item_count": item_count,
                    "is_current": embedding_model_id == chatbot.embedding_model_id
                })
        
        return {
            "collections": embedding_collections,
            "current_embedding_model": chatbot.embedding_model_id
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
    """Check if Ollama is running and responsive (deprecated - use /providers/ollama/status)."""
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


@app.get("/embedding_models")
def list_embedding_models():
    """List all available embedding models."""
    from backend.embed_utils import EMBEDDING_MODELS
    try:
        models = [
            {
                "id": model_id,
                **config
            }
            for model_id, config in EMBEDDING_MODELS.items()
        ]
        return {"models": models}
    except Exception as e:
        return {"error": str(e)}


@app.get("/providers")
def list_providers():
    """List all available LLM providers and their metadata."""
    from backend.model_providers import get_provider_info
    try:
        providers = get_provider_info()
        return {"providers": providers}
    except Exception as e:
        return {"error": str(e)}


@app.get("/providers/{provider_id}/models")
def list_provider_models(provider_id: str):
    """List available models for a specific provider."""
    from backend.model_providers import get_provider
    try:
        provider = get_provider(provider_id)
        if not provider:
            return {"error": f"Provider '{provider_id}' not found"}
        
        settings = load_settings()
        provider_config = settings.get("providers", {}).get(provider_id, {})
        credentials = provider_config.get("credentials", {})
        
        models = provider.list_models(credentials)
        
        return {
            "models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "description": m.description,
                    "context_length": m.context_length
                }
                for m in models
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/providers/{provider_id}/validate")
def validate_provider(provider_id: str, credentials: dict = Body(...)):
    """Validate credentials for a specific provider."""
    from backend.model_providers import get_provider
    try:
        provider = get_provider(provider_id)
        if not provider:
            return {"error": f"Provider '{provider_id}' not found", "valid": False}
        
        # Use provided credentials or get from settings
        creds = credentials.get("credentials", {})
        if not creds:
            settings = load_settings()
            provider_config = settings.get("providers", {}).get(provider_id, {})
            creds = provider_config.get("credentials", {})
        
        is_valid = provider.validate_credentials(creds)
        return {"valid": is_valid, "provider": provider_id}
    except Exception as e:
        error_msg = str(e)
        # Determine error type
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            return {"valid": False, "error": "Invalid credentials", "details": error_msg}
        elif "connection" in error_msg.lower():
            return {"valid": False, "error": "Connection failed", "details": error_msg}
        else:
            return {"valid": False, "error": error_msg}


@app.get("/providers/{provider_id}/status")
def provider_status(provider_id: str):
    """Check the status and availability of a specific provider."""
    from backend.model_providers import get_provider
    try:
        provider = get_provider(provider_id)
        if not provider:
            return {"status": "unknown", "error": f"Provider '{provider_id}' not found"}
        
        settings = load_settings()
        provider_config = settings.get("providers", {}).get(provider_id, {})
        
        if not provider_config.get("enabled"):
            return {
                "status": "disabled",
                "provider": provider_id,
                "message": "Provider is disabled in settings"
            }
        
        credentials = provider_config.get("credentials", {})
        
        try:
            is_valid = provider.validate_credentials(credentials)
            if is_valid:
                return {
                    "status": "available",
                    "provider": provider_id,
                    "label": provider.label
                }
            else:
                return {
                    "status": "unavailable",
                    "provider": provider_id,
                    "message": "Credentials validation failed"
                }
        except Exception as validation_error:
            return {
                "status": "error",
                "provider": provider_id,
                "message": str(validation_error)
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/settings")
def get_settings():
    """Get current application settings."""
    try:
        settings = load_settings()
        
        # Mask API keys for security - don't send full keys to frontend
        masked_settings = settings.copy()
        if "providers" in masked_settings:
            masked_providers = {}
            for provider_id, provider_config in masked_settings["providers"].items():
                masked_provider = provider_config.copy()
                if "credentials" in masked_provider:
                    masked_creds = masked_provider["credentials"].copy()
                    if "api_key" in masked_creds and masked_creds["api_key"]:
                        masked_creds["api_key"] = "***"
                    masked_provider["credentials"] = masked_creds
                masked_providers[provider_id] = masked_provider
            masked_settings["providers"] = masked_providers
        
        return masked_settings
    except Exception as e:
        return {"error": str(e)}


@app.get("/profiles")
def list_profiles():
    """List all available profiles."""
    try:
        profiles = profile_manager.list_profiles()
        active = profile_manager.get_active_profile()
        return {
            "profiles": profiles,
            "activeProfileId": active['id'] if active else None
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/profiles")
def create_profile(payload: dict = Body(...)):
    """Create a new profile.
    
    Expects JSON body: {"id": "my-profile", "name": "My Profile", "description": "Optional"}
    """
    try:
        profile_id = payload.get("id")
        name = payload.get("name")
        description = payload.get("description", "")
        
        if not profile_id or not name:
            return {"error": "Missing required fields: id, name"}
        
        metadata = profile_manager.create_profile(profile_id, name, description)
        return {"success": True, "profile": metadata}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/profiles/{profile_id}")
def get_profile(profile_id: str):
    """Get metadata for a specific profile."""
    try:
        profile = profile_manager.get_profile(profile_id)
        if not profile:
            return {"error": f"Profile '{profile_id}' not found"}
        return {"profile": profile}
    except Exception as e:
        return {"error": str(e)}


@app.put("/profiles/{profile_id}")
def update_profile(profile_id: str, payload: dict = Body(...)):
    """Update profile metadata.
    
    Expects JSON body: {"name": "New Name", "description": "New Description"}
    """
    try:
        name = payload.get("name")
        description = payload.get("description")
        
        success = profile_manager.update_profile(profile_id, name, description)
        if not success:
            return {"error": f"Profile '{profile_id}' not found"}
        
        return {"success": True, "profile": profile_manager.get_profile(profile_id)}
    except Exception as e:
        return {"error": str(e)}


@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str, force: bool = Query(False)):
    """Delete a profile and all its data."""
    try:
        success = profile_manager.delete_profile(profile_id, force=force)
        if not success:
            return {"error": f"Profile '{profile_id}' not found"}
        return {"success": True}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


@app.post("/profiles/{profile_id}/activate")
def activate_profile(profile_id: str):
    """Set the active profile."""
    try:
        success = profile_manager.set_active_profile(profile_id)
        if not success:
            return {"error": f"Profile '{profile_id}' not found"}
        
        # Reinitialize chatbot with new profile
        global chatbot
        chatbot = initialize_chatbot()
        
        return {
            "success": True,
            "activeProfile": profile_manager.get_active_profile()
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/profiles/{profile_id}/sessions")
def get_profile_sessions(profile_id: str):
    """Get sessions for a specific profile."""
    try:
        sessions_data = profile_manager.load_profile_sessions(profile_id)
        return sessions_data
    except Exception as e:
        return {"error": str(e)}


@app.post("/profiles/{profile_id}/sessions")
def save_profile_sessions(profile_id: str, sessions_data: dict = Body(...)):
    """Save sessions for a specific profile."""
    try:
        success = profile_manager.save_profile_sessions(profile_id, sessions_data)
        if not success:
            return {"error": "Failed to save sessions"}
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


@app.post("/settings")
def update_settings(settings: dict = Body(...)):
    """Update application settings."""
    try:
        current_settings = load_settings()
        
        # Deep copy to avoid mutation issues
        import copy
        updated_settings = copy.deepcopy(current_settings)
        
        # Handle masked API keys - preserve existing keys if "***" is sent
        # Process providers specially to handle credentials correctly
        if "providers" in settings:
            for provider_id, provider_config in settings.get("providers", {}).items():
                # Initialize provider if it doesn't exist
                if provider_id not in updated_settings["providers"]:
                    updated_settings["providers"][provider_id] = {
                        "enabled": False,
                        "credentials": {}
                    }
                
                # Update enabled status
                if "enabled" in provider_config:
                    updated_settings["providers"][provider_id]["enabled"] = provider_config["enabled"]
                
                # Handle credentials with masking logic
                if "credentials" in provider_config:
                    current_creds = updated_settings["providers"][provider_id].get("credentials", {})
                    new_creds = provider_config["credentials"]
                    
                    # Merge credentials, preserving masked keys
                    for key, value in new_creds.items():
                        if key == "api_key" and value == "***":
                            # Keep existing API key if new value is masked
                            if "api_key" in current_creds:
                                updated_settings["providers"][provider_id]["credentials"]["api_key"] = current_creds["api_key"]
                        else:
                            # Update with new value
                            updated_settings["providers"][provider_id]["credentials"][key] = value
        
        # Update top-level settings (but not providers, already handled)
        for key, value in settings.items():
            if key != "providers":
                updated_settings[key] = value
        
        if save_settings(updated_settings):
            # Update global paths if they changed
            global DB_PATH, CHROMA_PATH, chatbot
            if "zoteroPath" in settings:
                DB_PATH = settings["zoteroPath"]
            if "chromaPath" in settings:
                CHROMA_PATH = settings["chromaPath"]
            
            # Reinitialize chatbot with new provider or embedding settings
            if "activeProviderId" in settings or "activeModel" in settings or "embeddingModel" in settings:
                try:
                    provider_credentials = {}
                    for pid, pconfig in updated_settings.get("providers", {}).items():
                        if pconfig.get("enabled"):
                            provider_credentials[pid] = pconfig.get("credentials", {})
                    
                    # Update provider settings if changed
                    if "activeProviderId" in settings or "activeModel" in settings:
                        chatbot.update_provider_settings(
                            active_provider_id=updated_settings.get("activeProviderId", "ollama"),
                            active_model=updated_settings.get("activeModel"),
                            credentials=provider_credentials
                        )
                    
                    # Update embedding model if changed - requires new ChromaClient
                    if "embeddingModel" in settings:
                        new_embedding_model = updated_settings.get("embeddingModel", "bge-base")
                        old_embedding_model = chatbot.embedding_model_id
                        if new_embedding_model != old_embedding_model:
                            print(f"Switching embedding model from {old_embedding_model} to {new_embedding_model}")
                            print(f"Creating new ChromaClient with collection: zotero_lib_{new_embedding_model}")
                            chatbot.embedding_model_id = new_embedding_model
                            # Reinitialize ChromaClient with new embedding model
                            chroma_path = updated_settings.get("chromaPath", CHROMA_PATH)
                            chatbot.chroma = ChromaClient(chroma_path, embedding_model_id=new_embedding_model)
                        else:
                            print(f"Embedding model unchanged: {chatbot.embedding_model_id}")
                except Exception as e:
                    print(f"Warning: Failed to update chatbot settings: {e}")
            
            return {"success": True, "message": "Settings saved successfully"}
        else:
            return {"error": "Failed to save settings"}
    except Exception as e:
        return {"error": str(e)}


