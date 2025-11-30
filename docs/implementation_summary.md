# Snippets Panel Implementation - Summary

## Overview
Implemented a comprehensive "Evidence Panel" (Snippets Panel) that displays the provenance of LLM answers by showing the specific text chunks and metadata from PDFs that were used as context.

**Latest Update (Nov 30, 2025)**: Upgraded RAG retrieval system with:
- BGE-base embeddings (768-dim, state-of-the-art)
- Hybrid search combining dense + sparse retrieval
- Cross-encoder re-ranking for precision
- Page-aware PDF chunking with full provenance

See `docs/rag_improvements.md` for complete details.

## Changes Made

### 1. Type Definitions

#### `frontend/src/types/api.ts`
- Enhanced `Snippet` interface to include:
  - `snippet`: Main text field for the chunk
  - `title`, `authors`, `year`: Bibliographic metadata
  - `page`: Page number (optional)
  - `zoteroKey`: For Zotero URI construction
  - `pdf_path`: Local PDF file path

#### `frontend/src/types/session.ts`
- Updated `Snippet` type to include metadata fields:
  - `page`, `title`, `authors`, `year`
  - Maintains backward compatibility with existing fields

### 2. New Components

#### `frontend/src/components/sources/SnippetCard.tsx` (NEW)
A reusable component that displays individual snippets with:
- **Visual design**: Badge number, title, author/year metadata
- **Text display**: Monospace font with 350-character truncation
- **Expand/collapse**: "Show more/less" button for long snippets
- **Action buttons**:
  - "Open in Zotero": Launches Zotero app with item selected
  - "Open PDF": Opens PDF in system default viewer
- **Error handling**: Displays action errors inline

#### `frontend/src/utils/zotero.ts` (NEW)
Utility functions for Zotero integration:
- `buildZoteroSelectUri()`: Creates `zotero://select` URIs
- `buildZoteroOpenPdfUri()`: Creates `zotero://open-pdf` URIs with page support
- `tryOpenZoteroUri()`: Attempts to open Zotero URIs with fallbacks
- `openLocalPdf()`: Opens PDFs via backend `/open_pdf` endpoint

### 3. Updated Components

#### `frontend/src/features/sessions/SnippetsPanel.tsx` (COMPLETE REWRITE)
Completely redesigned from a user-snippet collection panel to an evidence/provenance panel:

**Before**: Showed user-saved snippets grouped by source, with "Insert" and "Star" buttons

**After**: Shows AI-generated evidence for the last answer with:
- Clear, informative states:
  - **No session**: Guidance to start a conversation
  - **Loading**: Spinner with "Retrieving source snippets..."
  - **Empty**: Friendly message when no snippets found
  - **Populated**: List of snippets in relevance order
- Integration with `ChatContext` for loading state
- Uses new `SnippetCard` component for consistent display
- Maintains collapsible sidebar functionality

#### `frontend/src/contexts/ChatContext.tsx`
Enhanced snippet data mapping to capture all metadata fields:
- Maps `s.snippet` (primary) or `s.text` (fallback) to snippet text
- Extracts and stores: `page`, `title`, `authors`, `year`
- Applies robust field mapping for both initial session creation and message appends
- Handles various backend response formats gracefully

#### `frontend/src/components/ui/Spinner.tsx`
- Added default export for backward compatibility

### 4. Documentation

#### `docs/snippets_panel.md` (NEW)
Comprehensive documentation including:
- Feature overview and key capabilities
- Architecture and component structure
- Data flow diagrams
- Type definitions
- Usage instructions for users and developers
- Design principles
- Future enhancement roadmap
- Troubleshooting guide

#### `docs/backend_snippet_format.md` (NEW)
Backend integration guide with:
- Example request/response JSON
- Field descriptions for citations and snippets
- Notes on citation IDs and ordering
- Backend implementation reference
- Testing instructions

## Key Features

### 🎯 Transparent Provenance
- Shows exact PDF passages used for each answer
- Displays snippets in order of relevance
- Full bibliographic metadata for each source

### 📚 Rich Metadata Display
- Paper title and authors
- Publication year
- Page numbers (when available)
- Snippet preview with expand/collapse

### 🔗 Quick Navigation
- Direct links to open items in Zotero
- One-click PDF viewing
- Graceful error handling for missing resources

### 🎨 Smart State Management
- Loading states with spinner
- Empty states with helpful guidance
- Error states with inline messages
- Responsive to chat context changes

## Technical Highlights

1. **Robust Data Mapping**: Handles various backend response formats with comprehensive fallbacks
2. **Separation of Concerns**: Clean component hierarchy with dedicated utility functions
3. **Type Safety**: Full TypeScript coverage with well-defined interfaces
4. **User Experience**: Thoughtful loading/empty/error states throughout
5. **Extensibility**: Designed to accommodate future features (annotations, tags, collections)

## Files Created

```
frontend/src/
├── components/
│   └── sources/
│       └── SnippetCard.tsx          (NEW)
├── utils/
│   └── zotero.ts                     (NEW)
docs/
├── snippets_panel.md                 (NEW)
└── backend_snippet_format.md         (NEW)
```

## Files Modified

```
frontend/src/
├── types/
│   ├── api.ts                        (Enhanced Snippet interface)
│   └── session.ts                    (Enhanced Snippet type)
├── contexts/
│   └── ChatContext.tsx               (Enhanced snippet mapping)
├── components/
│   └── ui/
│       └── Spinner.tsx               (Added default export)
└── features/
    └── sessions/
        └── SnippetsPanel.tsx         (Complete rewrite)
```

## Testing Checklist

- [x] TypeScript compilation successful (no errors)
- [x] All imports resolve correctly
- [x] Component structure is sound
- [ ] Runtime testing (requires backend):
  - [ ] Snippets display after chat response
  - [ ] Loading state appears during chat
  - [ ] Empty state shown when no snippets
  - [ ] "Open in Zotero" launches Zotero app
  - [ ] "Open PDF" opens PDF file
  - [ ] Expand/collapse works for long snippets
  - [ ] Metadata displays correctly

## Usage

1. Start the backend with snippet support
2. Open the frontend application
3. Ask a question in the chat
4. View the "Evidence" panel (left sidebar) to see source snippets
5. Click action buttons to navigate to sources

## Future Enhancements

Designed to support:
- User-created highlights/annotations
- Snippet search and filtering
- Export to notes
- Tag and collection display
- Direct PDF page navigation in Zotero reader

## Notes

- Backend already provides properly formatted snippet data (no backend changes needed)
- The panel is backward compatible - existing sessions will work but may not have snippet metadata
- The component gracefully handles missing or incomplete metadata
- All Zotero integrations respect group libraries and handle authentication transparently
