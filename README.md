# Zotero RAG Assistant

A desktop application that lets you chat with your Zotero library using large language models. Ask questions about your research and get answers grounded in your own documents, with citations and page numbers.

## What It Does

This tool indexes the PDFs in your Zotero library and uses retrieval-augmented generation (RAG) to answer questions based on their content. Every answer includes citations to the specific sources and page numbers used, making it easy to verify claims and follow up on interesting findings.

The application can run entirely on your local machine. Your documents and queries stay private.

## Key Features

- **Semantic search across your library**: Find relevant passages using natural language queries, not just keyword matching
- **Cited answers**: Responses include references to specific documents and page numbers
- **Source transparency**: View the exact text passages used to generate each answer
- **Multiple LLM providers**: Use local models via Ollama, or connect to OpenAI, Anthropic, Google, or other providers
- **Profile support**: Maintain separate workspaces with different settings and chat histories
- **Automatic updates**: Stay up to date with the latest features and improvements
- **Cross-platform**: Available for macOS, Windows, and Linux


<img width="1439" height="784" alt="Screenshot 2025-11-30 at 11 23 10 PM" src="https://github.com/user-attachments/assets/d27ea2ff-6337-48ce-8dca-0f9d11d22662" />

## Prerequisites

To use this application locally, you need:

### 1. Zotero Desktop Client

Install [Zotero](https://www.zotero.org/download/) and sync your library:
- The app reads your local Zotero database to access PDFs and metadata
- Make sure Zotero is installed and your library is synced before first launch
- Default database location:
  - **macOS:** `~/Zotero/zotero.sqlite`
  - **Windows:** `C:\Users\{username}\Zotero\zotero.sqlite`
  - **Linux:** `~/Zotero/zotero.sqlite`

### 2. Ollama (for local LLM support)

Install [Ollama](https://ollama.ai/) to run language models locally:

```bash
# macOS/Linux - Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/download
```

**Download models:**
```bash
# Recommended models for chat
ollama pull llama3.2       # Fast, general-purpose (3B)
ollama pull mistral        # Good balance (7B)
ollama pull llama3.1       # Best quality (8B/70B)

# Recommended embedding model (required for semantic search)
ollama pull nomic-embed-text
```

**Verify installation:**
```bash
ollama list
# Should show downloaded models
```

**Alternative:** You can also use cloud providers (OpenAI, Anthropic, Google) by configuring API keys in the app settings.


## Installation

### Desktop App (Recommended)

Download the latest installer from [Releases](https://github.com/aahepburn/Zotero-RAG-Assistant/releases):

#### macOS
1. Download `Zotero-RAG-Assistant-{version}-mac-arm64.dmg` (Apple Silicon) or `-mac-x64.dmg` (Intel)
2. Open the DMG file
3. Drag the app icon to the Applications folder
4. Since the app isn't signed by Apple, you will need to run this command in your Terminal first: `xattr -dr com.apple.quarantine "/Applications/Zotero RAG
 Assistant.app"`
5. Launch from Applications or Spotlight

**System Requirements:** macOS 10.13 (High Sierra) or later

#### Windows
1. Download `Zotero-RAG-Assistant-{version}-win-x64.exe`
2. Run the installer (may show SmartScreen warning on first run - click "More info" then "Run anyway")
3. Choose installation location (default: `C:\Users\{username}\AppData\Local\Programs\`)
4. Launch from Start Menu or desktop shortcut

**System Requirements:** Windows 10 or later (64-bit)

**Note:** Windows builds are now available but may show SmartScreen warnings since the app is not code-signed. See [docs/WINDOWS_BUILD_GUIDE.md](docs/WINDOWS_BUILD_GUIDE.md) for build instructions and troubleshooting.

#### Linux

**Debian/Ubuntu (Recommended)**
```bash
# Download the .deb package
wget https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.7/zotero-rag-assistant_0.1.7_amd64.deb

# Install (automatically handles dependencies)
sudo apt install ./zotero-rag-assistant_0.1.7_amd64.deb

# Launch from application menu or terminal
zotero-rag-assistant
```

**Other Distributions (AppImage)**
```bash
# Download AppImage
wget https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.7/Zotero-RAG-Assistant-0.1.7-linux-x64.AppImage

# Make executable and run
chmod +x Zotero-RAG-Assistant-0.1.7-linux-x64.AppImage
./Zotero-RAG-Assistant-0.1.7-linux-x64.AppImage
```

**System Requirements:** 
- Modern Linux distribution (Ubuntu 18.04+, Debian 10+, Fedora 28+, or equivalent)
- User namespaces enabled (default on most systems)
- See [docs/LINUX_PACKAGING.md](docs/LINUX_PACKAGING.md) for detailed Linux information

**Note:** All installers include Python and dependencies. No additional setup required.

### Run from Source (Developers)

For development or customization:

**Prerequisites:**
- Python 3.8+
- Node.js 16+
- Zotero with local library

**Setup:**
```bash
git clone https://github.com/aahepburn/Zotero-RAG-Assistant.git
cd Zotero-RAG-Assistant

# Python environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Node dependencies
npm install
cd frontend && npm install && cd ..

# Run development mode (all services)
npm run dev
```

See [docs/DESKTOP_APP.md](docs/DESKTOP_APP.md) for detailed development instructions.

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

For complete build instructions, see [docs/BUILD_CHECKLIST.md](docs/BUILD_CHECKLIST.md).

## Documentation

** [Complete Documentation Index](docs/README.md)**

**Quick Links:**
- **Users:** [Prompting Guide](docs/PROMPTING_QUICKSTART.md) · [Provider Setup](docs/provider_guide.md)
- **Developers:** [Build Checklist](docs/BUILD_CHECKLIST.md) · [Desktop App Guide](docs/DESKTOP_APP.md)
- **Platform-Specific:** [Windows Build](docs/WINDOWS_BUILD_GUIDE.md) · [Linux Packaging](docs/LINUX_PACKAGING.md)

## License

MIT

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes before submitting a pull request.
