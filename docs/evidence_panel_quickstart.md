# Quick Start: Using the Evidence Panel

## What is the Evidence Panel?

The Evidence Panel (formerly "Snippets Panel") shows you exactly which parts of your research papers were used to generate each answer. It provides transparency and lets you verify the AI's sources.

## How to Use It

### 1. Ask a Question
Type your research question in the chat, for example:
- "What are the main criticisms of transformer models?"
- "How does active learning reduce annotation costs?"
- "What methods are used for neural architecture search?"

### 2. View the Evidence
After receiving an answer, look at the **Evidence panel** on the left side. You'll see:

- **Numbered badges** (1, 2, 3...): Each snippet's relevance rank
- **Paper titles**: Which papers contributed to the answer
- **Authors and year**: Quick reference to identify sources
- **Text excerpts**: The actual passages used as context
- **Page numbers**: Where to find this content in the PDF (when available)

### 3. Navigate to Sources

Each snippet has action buttons:

#### "Open in Zotero" button
- **What it does**: Opens the Zotero desktop app and selects this item in your library
- **When to use**: When you want to see the full bibliographic details, tags, notes, or related items
- **Requirements**: Zotero desktop app must be running

#### "Open PDF" button
- **What it does**: Opens the PDF in your default PDF viewer
- **When to use**: When you want to read the full context around the snippet
- **Requirements**: The PDF must be stored locally (Zotero's file storage)

### 4. Read More Context

For long snippets:
- Click **"Show more"** to expand the full text
- Click **"Show less"** to collapse it again

## Understanding the Display

### Visual Elements

```
┌─────────────────────────────────────────┐
│ [1]  Active Learning Literature Survey  │
│      Settles, B. (2009)                  │
│                                           │
│  ┌─────────────────────────────────────┐│
│  │ "The key idea behind active          ││
│  │  learning is that a machine          ││
│  │  learning algorithm can..."          ││
│  └─────────────────────────────────────┘│
│                                           │
│  [Show more]                              │
│  [Open in Zotero]  [Open PDF]            │
└─────────────────────────────────────────┘
```

### Snippet Order

Snippets are shown in **relevance order** - the most relevant passages appear first. This means:
- Snippet #1 was the most important for answering your question
- Snippet #2 was second most important, and so on

This helps you prioritize which sources to investigate first.

## Panel States

### "No Active Session"
You haven't asked any questions yet. Start a conversation to see evidence!

### "Retrieving source snippets..."
The AI is processing your question. This usually takes 3-10 seconds.

### "No Source Snippets"
The AI couldn't find relevant passages in your library for this question. This might mean:
- The question is outside your library's scope
- You might need to add relevant papers
- Try rephrasing your question to better match your papers

## Tips for Best Results

### 1. Verify the Sources
Always check that the snippets actually support the answer. AI can sometimes misinterpret context.

### 2. Read the Full Context
Use "Open PDF" to read the surrounding paragraphs. The snippet might be part of a larger argument.

### 3. Follow the Citations
The snippets correspond to citation numbers [1], [2], [3] in the answer text.

### 4. Check Multiple Sources
When the AI cites multiple sources for a claim, review all the snippets to see if they truly agree.

### 5. Look for Page Numbers
When available, page numbers help you quickly locate the passage in the full PDF.

## Troubleshooting

### "Open in Zotero" doesn't work
- **Solution**: Make sure Zotero desktop app is running
- **Why**: The app needs to be active to handle the `zotero://` link

### "Open PDF" doesn't work
- **Possible causes**:
  - PDF file was moved or deleted
  - Permissions issue with the file
  - PDF is stored in Zotero cloud but not synced locally
- **Solution**: Open the item in Zotero first, then open the PDF from there

### No snippets appear
- **Check**: Did the chat response complete successfully?
- **Check**: Does your library contain papers related to the question?
- **Try**: Ask a question that's more clearly within your research domain

### Metadata is missing
Some older papers or imported items might not have complete metadata (authors, year, etc.). This is normal and doesn't affect the snippet's validity.

## Advanced: Keyboard Shortcuts (Future)

*Not yet implemented - planned features:*
- `E` - Toggle evidence panel
- `Cmd/Ctrl + K` - Jump to next snippet
- `Cmd/Ctrl + J` - Jump to previous snippet

## Privacy Note

All evidence and snippets are:
- ✅ Processed locally on your machine
- ✅ Stored in your browser's localStorage
- ✅ Never sent to external servers (beyond the LLM API)
- ✅ Only visible to you

Your research remains private and secure.

---

**Need help?** Check the full documentation in `docs/snippets_panel.md` or report issues on GitHub.
