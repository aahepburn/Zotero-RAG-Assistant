# Zotero LLM Plugin

**Make your entire Zotero library chat-ready, intelligent, and traceable — all with reliable citations and deep native integration. Built fully open-source, privacy-first, and optimized for digital humanities, social sciences, and STEM researchers.**

---

##  Project Vision

Researchers deserve to talk to their own libraries as easily as sending a message — with answers that cite not just papers, but books, notes, and highlights. Existing solutions are “good enough” for tinkerers, but not for rigorous, seamless research. This project bridges that gap with a **native, local-first Zotero LLM assistant**.

---

## Features (MVP and Beyond)

- **Native Zotero integration:** (Coming soon) Right in your Zotero sidebar, chat with your library without extra setup.
- **Backend foundation:** FastAPI Python backend that parses, embeds, and indexes your PDFs, notes, and highlights.
- **Advanced RAG retrieval:** State-of-the-art hybrid search combining:
  - BGE-base embeddings (768-dim, MTEB #1 ranked)
  - BM25 sparse retrieval for keyword matching
  - Cross-encoder re-ranking for precision
  - Page-aware chunking with full provenance
- **Citation-traceable answers:** Every LLM answer is supported with direct references to your actual library items with exact page numbers.
- **Evidence Panel:** See exactly which PDF passages and sources were used to generate each answer, with one-click navigation to Zotero or PDF files. Makes AI responses transparent and verifiable.
- **Full-text & semantic search:** Search using meaning, not just keywords, across all your literature.
- **Automatic metadata extraction:** Enriches items with missing DOIs, abstracts, or author info as you index.
- **Privacy-first:** No data leaves your device; built for offline, local workflows.
- **Export to Obsidian/Markdown:** Send cited answers or chat sessions directly to your research vault or notes.
- **Planned:**
    - Citation and influence graph visualization
    - Book review discovery from trusted sources (JSTOR, etc)
    - Support for collaborative and multi-user libraries

---

## Repository Structure

