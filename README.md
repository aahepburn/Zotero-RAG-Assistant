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

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Zotero desktop app with a local library

### Installation

```bash
# Clone the repository
git clone https://github.com/aahepburn/zotero-llm-plugin.git
cd zotero-llm-plugin

# Run the setup script
./setup.sh

# Or manually:
# 1. Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure your settings
cp .env.example .env
# Edit .env and set your ZOTERO_DB_PATH
```

### Configuration

1. **Zotero Database Path**: Edit `.env` or configure in Settings UI
   - macOS default: `/Users/YOUR_USERNAME/Zotero/zotero.sqlite`
   - Windows: `C:\Users\YOUR_USERNAME\Zotero\zotero.sqlite`
   - Linux: `~/Zotero/zotero.sqlite`

2. **LLM Provider** (choose one):
   - **Ollama** (recommended, free, local): Install from [ollama.ai](https://ollama.ai) and run `ollama serve`
   - **OpenAI**: Add API key in Settings
   - **Anthropic Claude**: Add API key in Settings
   - **Other providers**: Perplexity, Google, Groq, OpenRouter supported

3. **API Keys** (optional): Configure via the Settings UI after starting the app, or set in `.env`

### Running the Application

```bash
# Terminal 1: Start backend
source .venv/bin/activate
uvicorn backend.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### First Steps

1. **Index your library**: Click "Index Library" to process your PDFs
2. **Start chatting**: Ask questions about your research
3. **View sources**: Check the Evidence Panel to see citations and snippets
4. **Configure settings**: Adjust LLM provider, embedding model, and paths as needed

---

## Repository Structure

