# Snippets Panel - Evidence & Provenance Feature

## Overview

The Snippets Panel (also called "Evidence Panel") provides transparency and trustworthiness to LLM answers by displaying the specific text chunks and metadata from your Zotero library that were used as context for generating each response.

## Key Features

### 1. **Transparent Provenance**
- Shows exactly which PDF passages contributed to each answer
- Displays snippets in order of relevance (as determined by the RAG system)
- Each snippet includes full bibliographic metadata

### 2. **Rich Metadata Display**
For each snippet, the panel shows:
- **Title**: The paper/book title from Zotero
- **Authors**: First author (with "et al." for multiple authors)
- **Year**: Publication year
- **Page number**: When available from the chunking process
- **Snippet text**: The actual text chunk (350 character preview with expand/collapse)

### 3. **Quick Navigation**
Two action buttons per snippet:
- **Open in Zotero**: Opens the item in the Zotero desktop app using `zotero://select` URI
- **Open PDF**: Opens the PDF in your system's default viewer via the backend `/open_pdf` endpoint

### 4. **Smart State Management**
- **Loading state**: Shows spinner while waiting for chat response
- **Empty state**: Friendly message when no snippets are found
- **No session state**: Clear guidance when no chat session is active
- **Error handling**: Gracefully handles missing metadata or failed actions

## Architecture

### Component Structure

```
features/sessions/SnippetsPanel.tsx
├── Uses SessionsContext for session data
├── Uses ChatContext for loading state
└── Renders multiple SnippetCard components

components/sources/SnippetCard.tsx
├── Displays individual snippet with metadata
├── Handles text truncation (350 chars)
├── Manages expand/collapse state
└── Provides action buttons with error handling

utils/zotero.ts
├── buildZoteroSelectUri()
├── buildZoteroOpenPdfUri()
├── tryOpenZoteroUri()
└── openLocalPdf()
```

### Data Flow

1. **Backend Response**: `/chat` endpoint returns:
   ```typescript
   {
     summary: string,
     citations: Citation[],
     snippets: Snippet[]
   }
   ```

2. **ChatContext Processing**: Maps backend data to session snippets:
   ```typescript
   {
     id: string,
     sourceId: string,        // Links to citation
     text: string,            // The snippet content
     title: string,
     authors: string,
     year: string | number,
     page: number | string,
     locationHint: string
   }
   ```

3. **Session Storage**: Snippets are persisted in localStorage as part of session data

4. **Panel Display**: SnippetsPanel retrieves snippets and renders SnippetCard for each

### Type Definitions

**API Types** (`types/api.ts`):
```typescript
export interface Snippet {
  id: string;
  citation_id?: number;
  snippet: string;           // Main text field
  title: string;
  authors?: string;
  year?: string | number;
  page?: number | string;
  zoteroKey?: string;
  pdf_path?: string;
}
```

**Session Types** (`types/session.ts`):
```typescript
export type Snippet = {
  id: string;
  sourceId: string;
  text: string;
  title?: string;
  authors?: string;
  year?: string | number;
  page?: number | string;
  locationHint?: string;
};
```

## Usage

### For Users

1. Ask a question in the chat
2. Wait for the LLM response
3. View the "Evidence" panel (left sidebar) to see:
   - Which papers were cited
   - Exact passages used as context
   - Metadata for each source
4. Click "Open in Zotero" to view the full item
5. Click "Open PDF" to read the complete document

### For Developers

**Adding snippet data to backend responses:**

The backend `interface.py` already returns properly formatted snippets in the `chat()` method:

```python
snippets.append({
    "citation_id": cid,
    "snippet": snippet_text,
    "title": title,
    "year": year,
    "authors": authors,
    "pdf_path": pdf_path,
})
```

**Extending metadata fields:**

To add new metadata (e.g., tags, collections):

1. Update `types/api.ts` Snippet interface
2. Update `types/session.ts` Snippet type
3. Update `ChatContext.tsx` mapping logic
4. Update `SnippetCard.tsx` to display new fields
5. Update backend to include fields in response

## Design Principles

1. **Transparency First**: Make the provenance of answers immediately visible
2. **Non-Intrusive**: Don't block or distract from the main chat flow
3. **Graceful Degradation**: Handle missing metadata elegantly
4. **Progressive Disclosure**: Show previews, allow expansion for details
5. **Action-Oriented**: Provide quick access to source materials

## Future Enhancements

### Planned Features
- [ ] User-created highlights integration
- [ ] Annotation overlay on PDFs
- [ ] Snippet search and filtering
- [ ] Export snippets to notes
- [ ] Tag and collection metadata display
- [ ] Link to specific PDF pages in Zotero PDF reader

### Extensibility Considerations

The current implementation is designed to accommodate:
- **User annotations**: Can be merged into snippet display
- **Additional metadata**: Easy to add tags, collections, etc.
- **Custom sorting**: Relevance, date, author, etc.
- **Snippet interactions**: Copy, quote, save, etc.

## Testing

To verify the feature works correctly:

1. **Start the backend**: Ensure the chat endpoint returns snippets
2. **Ask a question**: Verify loading state appears
3. **Check snippet display**: Confirm metadata and text are shown
4. **Test "Open in Zotero"**: Should launch Zotero and select item
5. **Test "Open PDF"**: Should open PDF in default viewer
6. **Test truncation**: Long snippets should show "Show more" button
7. **Test empty state**: Delete snippets from session, verify message
8. **Test no session**: Clear session, verify appropriate message

## Troubleshooting

**Snippets not appearing:**
- Check backend response includes `snippets` array
- Verify ChatContext mapping logic
- Check browser console for errors

**"Open in Zotero" not working:**
- Ensure Zotero desktop app is running
- Verify `zoteroKey` is present in source metadata
- Check browser allows `zotero://` protocol handlers

**"Open PDF" failing:**
- Verify backend `/open_pdf` endpoint is working
- Check PDF path exists on filesystem
- Ensure backend has permissions to access file

**Metadata missing:**
- Backend may not be providing all fields
- Check `ChatContext.tsx` field mapping
- Verify backend chunking process preserves metadata

## Related Files

- `frontend/src/features/sessions/SnippetsPanel.tsx` - Main panel component
- `frontend/src/components/sources/SnippetCard.tsx` - Individual snippet display
- `frontend/src/utils/zotero.ts` - Zotero URI utilities
- `frontend/src/contexts/ChatContext.tsx` - Data mapping and session creation
- `frontend/src/types/api.ts` - Backend API types
- `frontend/src/types/session.ts` - Session data types
- `backend/interface.py` - Backend snippet generation (chat method)
