# Quick Fix Guide - Embedding Dimension Mismatch

## The Problem
```
Collection expecting embedding with dimension of 768, got 384
```

## Root Cause
Query methods were using ChromaDB's default embedder (384 dims) instead of your custom embedder (768 dims).

## The Fix (Already Applied)

### Changed in `vector_db.py`:
```python
# BEFORE (WRONG):
results = self.collection.query(query_texts=[query], ...)

# AFTER (CORRECT):
query_embedding = get_embedding(query)
results = self.collection.query(query_embeddings=[query_embedding.tolist()], ...)
```

## Steps to Resolve

1. **Delete old database:**
   ```bash
   rm -rf /Users/aahepburn/.zotero-llm/chroma/user-1
   ```

2. **Run test suite:**
   ```bash
   python3 -m backend.tests.test_embeddings
   ```
   Should show: `✓ ALL TESTS PASSED`

3. **Start backend:**
   ```bash
   uvicorn backend.main:app --reload
   ```

4. **Check health:**
   Visit: http://localhost:8000/db_health
   
   Should show:
   ```json
   {"status": "empty", "expected_dimension": 768}
   ```

5. **Re-index library** (use frontend button)

6. **Verify:**
   Visit: http://localhost:8000/db_health
   
   Should show:
   ```json
   {"status": "ok", "actual_dimension": 768}
   ```

## Why This Won't Happen Again

- ✓ All queries now use manual embeddings (same 768 dims as indexing)
- ✓ Dimension validation catches mismatches early
- ✓ Test suite verifies configuration
- ✓ Health endpoint monitors database status

## Verification
```bash
python3 -m backend.tests.test_embeddings
```

Expected output:
```
✓ ALL TESTS PASSED
Model: BAAI/bge-base-en-v1.5
Dimension: 768
```

## Quick Checks

| Check | Command | Expected Result |
|-------|---------|----------------|
| Tests pass | `python3 -m backend.tests.test_embeddings` | `✓ ALL TESTS PASSED` |
| DB empty | `curl http://localhost:8000/db_health` | `"status": "empty"` |
| DB healthy (after indexing) | `curl http://localhost:8000/db_health` | `"status": "ok"` |

## Need Help?

See full documentation: `docs/EMBEDDING_DIMENSION_FIX.md`
