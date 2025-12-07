# Zotero RAG Assistant

A desktop application that lets you chat with your Zotero library using large language models. Ask questions about your research and get answers grounded in your own documents, with citations and page numbers.

## What It Does

This tool indexes the PDFs in your Zotero library and uses retrieval-augmented generation (RAG) to answer questions based on their content. Every answer includes citations to the specific sources and page numbers used, making it easy to verify claims and follow up on interesting findings.

The application runs entirely on your local machine. Your documents and queries stay private.

## Key Features

- **Semantic search across your library**: Find relevant passages using natural language queries, not just keyword matching
- **Cited answers**: Responses include references to specific documents and page numbers
- **Source transparency**: View the exact text passages used to generate each answer
- **Multiple LLM providers**: Use local models via Ollama, or connect to OpenAI, Anthropic, Google, or other providers
- **Profile support**: Maintain separate workspaces with different settings and chat histories
- **Automatic updates**: Stay up to date with the latest features and improvements
- **Cross-platform**: Available for macOS, Windows, and Linux


<img width="1439" height="784" alt="Screenshot 2025-11-30 at 11 23 10 PM" src="https://github.com/user-attachments/assets/d27ea2ff-6337-48ce-8dca-0f9d11d22662" />


## Installation

### Option 1: Desktop App (Recommended)

Download the installer for your platform from the [Releases](https://github.com/aahepburn/zotero-llm-plugin/releases) page:

- **macOS**: Download the `.dmg` file and drag the app to your Applications folder
- **Windows**: Download and run the `.exe` installer
- **Linux**: Download the `.AppImage` file, make it executable (`chmod +x`), and run
  - **Note**: The AppImage includes Python, but if it fails to detect the bundled version, it will automatically use your system Python 3. Most modern Linux distros have Python 3 pre-installed. See [Linux Python Guide](docs/LINUX_PYTHON_GUIDE.md) if you encounter Python-related errors.

The desktop app includes all dependencies and will automatically check for updates. You can install new versions directly from the Settings page.

### Option 2: Run from Source

If you want to modify the code or prefer not to use the packaged app:

**Prerequisites:**
- Python 3.8 or later
- Node.js 16 or later
- Zotero with a local library

**Setup:**

```bash
git clone https://github.com/aahepburn/Zotero-RAG-Assistant.git
cd zotero-llm-plugin

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install
cd frontend && npm install && cd ..

# Start the application
npm run dev  # Runs frontend, backend, and Electron concurrently
```

For web-only development without Electron:

```bash
# Terminal 1: Backend
source .venv/bin/activate
uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

Then open http://localhost:5173 in your browser.

## Configuration

### First-Time Setup

1. **Zotero Database Location**: The app needs to know where your Zotero database is located. Set this in the Settings panel or in a `.env` file:
   - macOS: `/Users/YOUR_USERNAME/Zotero/zotero.sqlite`
   - Windows: `C:\Users\YOUR_USERNAME\Zotero\zotero.sqlite`
   - Linux: `~/Zotero/zotero.sqlite`

2. **Choose an LLM Provider**:
   - **Ollama** (recommended for local use): Install from [ollama.ai](https://ollama.ai), then run `ollama pull llama3` or another model
   - **OpenAI, Anthropic, etc.**: Add your API key in Settings

3. **Index Your Library**: Click "Index Library" to process your PDFs. This creates embeddings for semantic search. Initial indexing may take a while depending on library size.

### Using the App

- Type questions in natural language: "What methods are used to study X?" or "Compare the arguments about Y in my readings"
- View citations in the Evidence Panel to see which documents and pages were used
- Click document titles to open them in Zotero or your PDF reader
- Create multiple profiles if you work with different document collections

## Technical Details

**Architecture:**
- Backend: FastAPI (Python) with ChromaDB for vector storage
- Frontend: React with TypeScript
- Desktop: Electron wrapper with auto-updates
- Embeddings: BGE-base (768-dimensional) with hybrid BM25 keyword search
- Retrieval: Cross-encoder re-ranking for improved precision

**Privacy:**
All processing happens locally. If you use a cloud LLM provider (OpenAI, Anthropic, etc.), your queries and retrieved document chunks are sent to their API, but your full library never leaves your machine.

## Building Installers

To create distribution packages:

```bash
npm run package:mac      # macOS .dmg and .zip
npm run package:win      # Windows .exe installer
npm run package:linux    # Linux .AppImage and .deb
npm run package:all      # All platforms
```

Built packages appear in the `release/` directory.

See [docs/DESKTOP_APP.md](docs/DESKTOP_APP.md) for more details on the build process.

## Documentation

- [Desktop App Development](docs/DESKTOP_APP.md)
- [Auto-Updates System](docs/AUTO_UPDATES.md) - Complete guide to the automatic update system
- [Auto-Updates Quick Start](docs/AUTO_UPDATES_QUICKSTART.md) - Quick reference for users and developers
- [Python Detection & Bundling](docs/PYTHON_DETECTION.md) - Technical details on cross-platform Python handling
- [Linux Python Guide](docs/LINUX_PYTHON_GUIDE.md) - User guide for Linux AppImage Python requirements
- [API Endpoints](docs/api_endpoints.md)
- [Profile System](docs/profile_system_guide.md)
- [Multi-Provider Setup](docs/multi_provider_system.md)
- [RAG System Details](docs/rag_improvements.md)

## License

MIT

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes before submitting a pull request.
