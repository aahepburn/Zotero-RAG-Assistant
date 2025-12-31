# Sync Feature Diagnostics & Improvements

## Overview
This document describes improvements made to diagnose and fix issues with the sync feature getting stuck, showing items that won't index.

## Problem
The sync button was showing "SYNC (2)" indicating 2 items needed indexing, but clicking sync didn't resolve the issue. Items were being silently skipped during indexing with no feedback to the user.

## Root Cause Analysis

### How Sync Works
1. **Frontend**: Polls `/index_stats` every 30 seconds to get `new_items` count
2. **Backend**: Calculates `new_items = zotero_items - indexed_items`
3. **Indexing**: When sync is clicked, processes each new item through:
   - PDF text extraction
   - Text chunking with page tracking
   - Embedding generation
   - Storage in ChromaDB
   - BM25 index rebuild

### Why Items Get Stuck
Items were being marked as "processed" but never actually indexed due to:
- Missing or inaccessible PDF files
- Empty PDFs with no extractable text
- PDF extraction failures (corrupt files)
- Embedding generation errors
- ChromaDB storage failures

**Critical Issue**: These failures were silent - items were skipped without any error reporting, so they continued to show as "new" items indefinitely.

## Improvements Implemented

### 1. Comprehensive Error Logging (Backend)

**File**: `backend/interface.py`

Added detailed tracking and logging for:
- ✅ Missing PDF files with full path
- ✅ PDF extraction failures with exception details
- ✅ Empty pages data
- ✅ Chunking failures
- ✅ Embedding generation errors
- ✅ Embedding dimension mismatches
- ✅ ChromaDB storage failures

**New Feature**: `skip_reasons` array in `index_progress` tracks all failures with item IDs and specific error messages.

**Output Example**:
```
SKIPPED: Item 12345: PDF not found at /path/to/file.pdf
ERROR: Item 67890: PDF extraction failed - [Errno 2] No such file or directory
SUCCESS: Indexed item 11111 with 42 chunks

=== Indexing Summary ===
Total items attempted: 5
Successfully indexed: 3
Skipped/Failed: 2

Skip reasons:
  - Item 12345: PDF not found at /path/to/file.pdf
  - Item 67890: PDF extraction failed - [Errno 2] No such file or directory
========================
```

### 2. Diagnostic Endpoint (Backend)

**File**: `backend/main.py`

New endpoint: `GET /diagnose_unindexed`

Returns detailed diagnostics for each unindexed item:
```json
{
  "unindexed_count": 2,
  "diagnostics": [
    {
      "item_id": "12345",
      "title": "Research Paper Title",
      "pdf_path": "/path/to/file.pdf",
      "pdf_exists": false,
      "issues": ["PDF file not found at: /path/to/file.pdf"]
    }
  ]
}
```

This helps identify:
- Which specific items won't index
- Why each item is failing
- Whether PDFs exist and are readable
- Text extraction capability

### 3. Frontend Skip Reasons Display

**File**: `frontend/src/components/layout/TopNav.tsx`

**Visual Feedback**: When items are skipped during indexing, a warning box appears showing:
- Number of items skipped
- First 3 skip reasons with item IDs
- Indication if more items were skipped

**Diagnostic Button**: In the sync dropdown menu, a new "🔍 Diagnose Sync Issues" button appears when `new_items > 0`:
- Fetches diagnostics for unindexed items
- Logs detailed information to console
- Provides immediate user feedback

### 4. Success Logging

Both incremental and full reindex now log:
- `SUCCESS: Indexed item {id} with {n} chunks` for each successfully indexed item
- Final summary with success/failure counts
- Complete list of skip reasons

## How to Use

### For Users

1. **Check Sync Status**:
   - Look at sync button: `Sync (N)` means N items need indexing
   - Click dropdown arrow next to sync button for options

2. **Diagnose Issues**:
   - Click "🔍 Diagnose Sync Issues" in sync dropdown
   - Check browser console (F12) for detailed diagnostics
   - Review which PDFs are missing or problematic

3. **During Indexing**:
   - Watch for orange warning box showing skipped items
   - Check progress bar and item counts
   - Review skip reasons in real-time

4. **After Indexing**:
   - If sync count doesn't go to 0, items failed to index
   - Run diagnostics to see specific issues
   - Fix underlying problems (missing PDFs, file permissions, etc.)

### For Developers

**Check Backend Logs**:
```bash
# During indexing, you'll see:
SKIPPED: Item 123: PDF not found at /path
ERROR: Item 456: PDF extraction failed - error details
SUCCESS: Indexed item 789 with 42 chunks

=== Indexing Summary ===
Total items attempted: 10
Successfully indexed: 8
Skipped/Failed: 2
```

**Call Diagnostic Endpoint**:
```bash
curl http://localhost:5050/diagnose_unindexed
```

**Access Skip Reasons via API**:
```bash
curl http://localhost:5050/index_status
# Returns: { "status": "indexing", "progress": { "skip_reasons": [...] } }
```

## Common Issues & Solutions

### Issue: "PDF not found"
**Solution**: 
- Verify Zotero database path is correct
- Check PDF attachments exist in Zotero storage
- Ensure file permissions allow reading

### Issue: "PDF extraction failed"
**Solution**:
- PDF may be corrupt - try opening in PDF viewer
- PDF may be image-based (no text layer) - needs OCR
- File permissions issue - check read access

### Issue: "No pages data available"
**Solution**:
- PDF has no extractable text (scanned images)
- Empty PDF file
- PDF format not supported by extraction library

### Issue: "Embedding generation failed"
**Solution**:
- Check embedding model is available
- Verify embedding service is running (Ollama, etc.)
- Check network connectivity for remote services

### Issue: "Failed to add to ChromaDB"
**Solution**:
- Check disk space
- Verify ChromaDB path permissions
- Check for database corruption

## Technical Details

### Skip Tracking Implementation

```python
# In index_progress dict:
{
    "skip_reasons": [
        "Item 123: PDF not found at /path",
        "Item 456: No chunks created from pages data"
    ]
}
```

### Error Handling Pattern

```python
try:
    # Attempt operation (extract, embed, store)
    result = operation(item)
    print(f"SUCCESS: {item_id}")
except Exception as e:
    skip_reason = f"Item {item_id}: Operation failed - {str(e)}"
    print(f"ERROR: {skip_reason}")
    self.index_progress["skip_reasons"].append(skip_reason)
    continue  # Move to next item
```

## Testing

To test the improvements:

1. **Create a problematic item**:
   - Add a Zotero item with missing PDF
   - Try to sync

2. **Observe logging**:
   - Check backend terminal for SKIPPED/ERROR messages
   - Check frontend for warning box during indexing

3. **Run diagnostics**:
   - Click diagnostic button
   - Verify console output shows issue details

4. **Fix and retry**:
   - Correct the underlying issue
   - Re-run sync
   - Verify item indexes successfully

## Future Enhancements

Potential improvements:
- [ ] Modal dialog with full diagnostic details in UI
- [ ] "Skip and continue" vs "Fix and retry" options
- [ ] Automatic retry logic for transient failures
- [ ] PDF repair/OCR suggestions for image-based PDFs
- [ ] Batch operations to fix multiple items at once
- [ ] Export diagnostic report as JSON/CSV
