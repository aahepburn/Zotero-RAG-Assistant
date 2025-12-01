# Multiple Embedding Models Support

## Overview

The Zotero LLM Plugin now supports using multiple embedding models without conflicts. Each embedding model creates its own separate vector database collection, allowing you to:

- Switch between embedding models without losing your indexed data
- Compare different embedding models' performance
- Index your library with multiple models simultaneously

## How It Works

### Collection Naming

Each embedding model gets its own ChromaDB collection with a unique name:
- `zotero_lib_bge-base` - For BGE-Base model (768 dimensions)
- `zotero_lib_specter` - For SPECTER model (768 dimensions)
- `zotero_lib_minilm-l6` - For MiniLM-L6 model (384 dimensions)
- `zotero_lib_minilm-l3` - For MiniLM-L3 model (384 dimensions)

### BM25 Indexes

Each embedding model also maintains its own BM25 sparse retrieval index:
- `bm25_index_bge-base.pkl`
- `bm25_index_specter.pkl`
- `bm25_index_minilm-l6.pkl`
- `bm25_index_minilm-l3.pkl`

## Switching Embedding Models

### In Settings

1. Go to Settings
2. Change the **Embedding Model** dropdown
3. Click **Save Settings**
4. The system will automatically switch to the collection for that model

### First Time Using a Model

If you switch to an embedding model that hasn't been used yet:
1. The collection will be empty (0 items indexed)
2. Go to the main screen
3. Click **Index Library** (or **Full Reindex**)
4. Your library will be indexed with the new embedding model

### Switching Back

You can switch back to a previously used embedding model at any time:
- All your previous indexing work is preserved
- The system instantly switches to that model's collection
- No re-indexing needed

## API Endpoints

### Check Current Status

```bash
GET /index_stats
```

Returns:
```json
{
  "indexed_items": 42,
  "total_chunks": 1234,
  "zotero_items": 50,
  "new_items": 8,
  "needs_sync": true,
  "current_embedding_model": "bge-base",
  "collection_name": "zotero_lib_bge-base"
}
```

### List All Collections

```bash
GET /embedding_collections
```

Returns:
```json
{
  "collections": [
    {
      "collection_name": "zotero_lib_bge-base",
      "embedding_model_id": "bge-base",
      "item_count": 5420,
      "is_current": true
    },
    {
      "collection_name": "zotero_lib_minilm-l6",
      "embedding_model_id": "minilm-l6",
      "item_count": 5420,
      "is_current": false
    }
  ],
  "current_embedding_model": "bge-base"
}
```

## Storage Considerations

Each embedding model requires separate storage:
- **768-dimensional models** (BGE-Base, SPECTER): ~500-800 MB per 1000 documents
- **384-dimensional models** (MiniLM): ~250-400 MB per 1000 documents

If you have a large library and test multiple models, you may want to periodically clean up unused collections.

## Benefits

### No More Dimension Mismatch Errors

Previously, changing embedding models would cause errors like:
```
embedding with dimension 384 doesn't match existing collection dimension 768
```

Now each model has its own collection, so this error is impossible.

### Easy Comparison

You can:
1. Index with BGE-Base (high quality)
2. Index with MiniLM-L3 (fast)
3. Switch between them to compare retrieval quality
4. Keep both indexed for different use cases

### Zero Downtime Switching

- No need to delete and re-index when switching
- Instant switching between models
- All data preserved

## Technical Details

### Implementation

The `ChromaClient` class now accepts an `embedding_model_id` parameter:

```python
# Creates collection: zotero_lib_bge-base
chroma = ChromaClient(
    db_path="/path/to/chroma",
    embedding_model_id="bge-base"
)
```

### Metadata

Each collection stores its embedding model in metadata:

```python
{
    "hnsw:space": "cosine",
    "embedding_model": "bge-base"
}
```

This allows future validation and debugging.

## Migration from Old Version

If you were using the plugin before this feature:
1. Your existing collection is named `zotero_lib` (no model suffix)
2. It likely uses `bge-base` embeddings (default)
3. When you first run with the new version, a new collection `zotero_lib_bge-base` will be created
4. You may want to delete the old `zotero_lib` collection to save space
5. Or run a full reindex to populate the new model-specific collection

## Future Enhancements

Potential improvements:
- Automatic migration of old `zotero_lib` collection
- UI showing which models are indexed
- Bulk delete of unused collections
- Collection export/import for sharing embeddings
