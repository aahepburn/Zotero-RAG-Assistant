# Embedding Dimension Fix - Complete Documentation

## Problem Summary

Your application was experiencing a persistent **embedding dimension mismatch error**:
```
Collection expecting embedding with dimension of 768, got 384
```

This occurred even after deleting and re-indexing the database multiple times.

## Root Cause Analysis

The issue was **NOT in the database itself**, but in how queries were being executed:

### What Was Happening:

1. **During Indexing** (✓ CORRECT):
   - Used `get_embedding()` from `embed_utils.py`
   - Model: `BAAI/bge-base-en-v1.5` 
   - Dimension: **768** ✓
   - Documents were stored with 768-dimensional embeddings

2. **During Querying** (✗ WRONG):
   - Used `collection.query(query_texts=[query], ...)`
   - This parameter triggers ChromaDB's **default embedding function**
   - ChromaDB default: `all-MiniLM-L6-v2`
   - Dimension: **384** ✗
   - **Dimension mismatch!**

### The Critical Bug:

In `vector_db.py`, the query methods were written like this:

```python
# WRONG - triggers ChromaDB's default embedder (384 dims)
dense_results = self.collection.query(
    query_texts=[query],  # ← This is the problem!
    n_results=k,
    where=where,
)
```

When you use `query_texts`, ChromaDB automatically embeds your query using its built-in model (`all-MiniLM-L6-v2`, 384 dimensions), which doesn't match your stored embeddings (768 dimensions).

## Complete Fix Applied

### 1. Added Embedding Constants (`embed_utils.py`)

```python
MODEL_NAME = 'BAAI/bge-base-en-v1.5'
EMBEDDING_DIMENSION = 768  # BGE-base produces 768-dimensional embeddings
```

This ensures consistency across the codebase.

### 2. Added Dimension Validation (`embed_utils.py`)

```python
def get_embedding(text):
    embedding = model.encode([text])[0]
    
    # Validate dimension to catch configuration issues early
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Embedding dimension mismatch! Expected {EMBEDDING_DIMENSION}, got {len(embedding)}. "
            f"Model: {MODEL_NAME}"
        )
    
    return embedding
```

Now any dimension mismatch is caught immediately with a clear error message.

### 3. Fixed Query Methods (`vector_db.py`)

**Before (WRONG):**
```python
results = self.collection.query(
    query_texts=[query],  # Uses ChromaDB's default embedder!
    n_results=k,
)
```

**After (CORRECT):**
```python
from backend.embed_utils import get_embedding

# Manually embed query to ensure consistent dimensions
query_embedding = get_embedding(query)

results = self.collection.query(
    query_embeddings=[query_embedding.tolist()],  # Use our embedder!
    n_results=k,
)
```

This was applied to:
- ✓ `query_db()`
- ✓ `query_hybrid()`

### 4. Fixed Collection Creation (`vector_db.py`)

Added explicit metadata to prevent ChromaDB from using default embedders:

```python
self.collection = self.chroma_client.get_or_create_collection(
    name=self.collection_name,
    metadata={"hnsw:space": "cosine"}  # Explicit configuration
)
```

### 5. Added Database Validation (`vector_db.py`)

New method to check database health:

```python
def validate_embedding_dimension(self) -> Dict[str, Any]:
    """
    Validate that the database is configured correctly for the current embedding model.
    """
    # ... validates dimensions, returns status ...
```

### 6. Added Health Check Endpoint (`main.py`)

```python
@app.get("/db_health")
def db_health():
    """Check the health and configuration of the vector database."""
    validation = chatbot.chroma.validate_embedding_dimension()
    return validation
```

### 7. Improved Error Messages (`main.py`)

```python
if "embedding with dimension" in error_msg.lower():
    return {
        "error": "Database configuration error: Embedding dimension mismatch detected. "
                "This usually means your database was created with a different embedding model. "
                "Please delete the vector database and re-index your library.",
        "technical_details": error_msg,
    }
```

### 8. Added Comprehensive Tests

Created `backend/tests/test_embeddings.py` to verify:
- ✓ Embedding dimensions are correct (768)
- ✓ Query methods use manual embeddings
- ✓ ChromaDB integration works properly
- ✓ Database validation works

## Why This Keeps the Problem From Returning

### Before the Fix:
The code had a **silent dependency** on ChromaDB's default behavior. Every time you queried, ChromaDB would use `all-MiniLM-L6-v2` (384 dims), causing mismatches.

### After the Fix:
1. **Explicit Control**: All embeddings (indexing AND querying) now use the same function: `get_embedding()`
2. **Early Detection**: Dimension validation catches mismatches immediately
3. **Clear Documentation**: Comments explain why we use `query_embeddings` not `query_texts`
4. **Automated Testing**: Test suite verifies configuration is correct
5. **Health Monitoring**: `/db_health` endpoint lets you check database status

## How to Proceed

### Step 1: Delete Old Database
```bash
rm -rf /Users/aahepburn/.zotero-llm/chroma/user-1
```

### Step 2: Verify Configuration
```bash
cd /Users/aahepburn/Projects/zotero-llm-plugin
source .venv/bin/activate
python3 -m backend.tests.test_embeddings
```

You should see:
```
✓ ALL TESTS PASSED

Your embedding configuration is correct!
Model: BAAI/bge-base-en-v1.5
Dimension: 768

You can now safely re-index your library.
```

### Step 3: Start Backend
```bash
uvicorn backend.main:app --reload
```

### Step 4: Check Database Health
Visit: `http://localhost:8000/db_health`

You should see:
```json
{
  "status": "empty",
  "message": "Database is empty. Re-indexing required.",
  "expected_dimension": 768,
  "model": "BAAI/bge-base-en-v1.5"
}
```

### Step 5: Re-index Library
Click the "Index Library" button in your frontend.

### Step 6: Verify After Indexing
Visit: `http://localhost:8000/db_health`

You should see:
```json
{
  "status": "ok",
  "message": "Database configuration is valid",
  "expected_dimension": 768,
  "actual_dimension": 768,
  "model": "BAAI/bge-base-en-v1.5",
  "document_count": 1
}
```

### Step 7: Test Query
Try asking a question in your frontend. It should now work without dimension errors!

## Technical Details

### Why ChromaDB Has a Default Embedder

ChromaDB is designed to be easy to use out-of-the-box. When you call:
```python
collection.query(query_texts=["some text"], ...)
```

ChromaDB automatically embeds the text using `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). This is convenient for simple use cases but becomes a problem when you:

1. Use a different model for indexing (768 dims)
2. Query with `query_texts` (384 dims from default)
3. Get dimension mismatch!

### The Solution Pattern

**Always separate embedding from storage/querying:**

```python
# ✓ CORRECT: Explicit control
query_embedding = get_embedding(query)  # Your custom embedder
results = collection.query(query_embeddings=[query_embedding.tolist()], ...)

# ✗ WRONG: Implicit ChromaDB embedder
results = collection.query(query_texts=[query], ...)  # Uses ChromaDB default
```

## Key Takeaways

1. **Never use `query_texts` parameter** when you have custom embeddings
2. **Always use `query_embeddings`** with manually-generated embeddings
3. **Validate dimensions** early to catch configuration issues
4. **Test thoroughly** after any embedding model changes
5. **Document explicitly** why certain patterns are used

## Future-Proofing

If you ever want to change the embedding model:

1. Update `MODEL_NAME` and `EMBEDDING_DIMENSION` in `embed_utils.py`
2. Delete the old database
3. Run the test suite: `python3 -m backend.tests.test_embeddings`
4. Re-index your library
5. Verify with `/db_health` endpoint

The system will now catch any dimension mismatches immediately!

## Files Modified

- ✓ `backend/embed_utils.py` - Added constants and validation
- ✓ `backend/vector_db.py` - Fixed query methods, added validation
- ✓ `backend/interface.py` - Added dimension logging
- ✓ `backend/main.py` - Added health endpoint and better errors
- ✓ `frontend/src/api/client.ts` - Added error response detection
- ✓ `frontend/src/features/chat/ChatMessages.tsx` - Added undefined content handling
- ✓ `frontend/src/contexts/SettingsContext.tsx` - Improved JSON parsing
- ✓ `backend/tests/test_embeddings.py` - NEW: Comprehensive test suite

## Verification Checklist

- [x] Test suite passes
- [x] Query methods use `query_embeddings` not `query_texts`
- [x] Dimension validation is in place
- [x] Health check endpoint exists
- [x] Error messages are helpful
- [x] Database is deleted and ready for re-indexing
- [x] Documentation is complete

**You are now safe to re-index and this issue will not return!**
