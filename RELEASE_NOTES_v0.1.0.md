# 🎉 Zotero LLM Assistant v0.1.0 - Desktop App Release

The Zotero LLM Plugin is now a **native desktop application**! Chat with your research library using AI - no manual setup required.

## ✨ What's New

### 🖥️ Native Desktop App
- **One-click installation** - Download, install, and run. No Python, Node.js, or command line needed!
- **Cross-platform support** - macOS (Intel & Apple Silicon), Windows (64-bit & 32-bit), and Linux (x64 & ARM64)
- **Bundled backend** - Everything you need is included in the installer
- **Native look & feel** - Integrates with your operating system

### 🔄 Automatic Updates
- Future updates download and install automatically
- No need to manually check for new versions
- One-click update notifications

### 🚀 Performance & Reliability
- Faster startup with optimized bundling
- Better process management - backend starts automatically
- Graceful shutdown - no orphaned processes
- Enhanced error handling and user notifications

### 🎨 User Experience
- Professional installers for each platform
- App icons in dock/taskbar (using default Electron icon for now)
- Native window controls
- Better integration with system features

## 📥 Download

Choose the installer for your platform:

| Platform | Download | Size | Notes |
|----------|----------|------|-------|
| **macOS (Apple Silicon)** | [Zotero-LLM-Assistant-0.1.0-mac-arm64.dmg](https://github.com/aahepburn/zotero-llm-plugin/releases/download/v0.1.0/Zotero%20LLM%20Assistant-0.1.0-mac-arm64.dmg) | 106 MB | M1/M2/M3/M4 Macs |
| **macOS (Intel)** | [Zotero-LLM-Assistant-0.1.0-mac-x64.dmg](https://github.com/aahepburn/zotero-llm-plugin/releases/download/v0.1.0/Zotero%20LLM%20Assistant-0.1.0-mac-x64.dmg) | 111 MB | Intel-based Macs |
| **Windows** | [Zotero-LLM-Assistant-0.1.0-win.exe](https://github.com/aahepburn/zotero-llm-plugin/releases/download/v0.1.0/Zotero%20LLM%20Assistant-0.1.0-win.exe) | 171 MB | Windows 10/11 |
| **Linux (x64)** | [Zotero-LLM-Assistant-0.1.0-linux-x86_64.AppImage](https://github.com/aahepburn/zotero-llm-plugin/releases/download/v0.1.0/Zotero%20LLM%20Assistant-0.1.0-linux-x86_64.AppImage) | 111 MB | Ubuntu 20.04+ |
| **Linux (ARM64)** | [Zotero-LLM-Assistant-0.1.0-linux-arm64.AppImage](https://github.com/aahepburn/zotero-llm-plugin/releases/download/v0.1.0/Zotero%20LLM%20Assistant-0.1.0-linux-arm64.AppImage) | 112 MB | Raspberry Pi 4+, ARM servers |

### Alternative Downloads
- macOS: [ZIP files](https://github.com/aahepburn/zotero-llm-plugin/releases/tag/v0.1.0) for manual installation
- Linux: [tar.gz archives](https://github.com/aahepburn/zotero-llm-plugin/releases/tag/v0.1.0) for advanced users

## 🚀 Getting Started

### Installation

**macOS:**
1. Download the `.dmg` file for your Mac (Intel or Apple Silicon)
2. Open the DMG and drag the app to your Applications folder
3. Launch "Zotero LLM Assistant" from Applications
4. If you see a security warning, go to System Settings > Privacy & Security and click "Open Anyway"

**Windows:**
1. Download the `.exe` installer
2. Run the installer (if Windows SmartScreen appears, click "More info" → "Run anyway")
3. Choose installation directory and complete setup
4. Launch from Start Menu or Desktop shortcut

**Linux:**
1. Download the `.AppImage` file
2. Make it executable: `chmod +x "Zotero LLM Assistant-0.1.0-linux-x86_64.AppImage"`
3. Run it: `./Zotero\ LLM\ Assistant-0.1.0-linux-x86_64.AppImage`

### First-Time Setup

After launching the app:

1. **Set Zotero Database Path**
   - Open Settings
   - Point to your Zotero database (usually `~/Zotero/zotero.sqlite`)
   
2. **Choose LLM Provider**
   - **Ollama** (recommended for local/free): Install from [ollama.ai](https://ollama.ai)
   - **OpenAI**: Add your API key in Settings
   - **Claude**: Add your Anthropic API key in Settings
   - **Other providers**: Perplexity, Google, Groq, OpenRouter supported

3. **Index Your Library**
   - Click "Index Library" to process your PDFs
   - First indexing may take some time depending on library size
   - Subsequent indexes are incremental (only new items)

4. **Start Chatting!**
   - Ask questions about your research
   - View cited sources in the Evidence Panel
   - Open PDFs directly from citations

## 📋 System Requirements

- **macOS**: 10.13 (High Sierra) or later
- **Windows**: Windows 10 or later (64-bit recommended)
- **Linux**: Ubuntu 20.04+, Debian 10+, or compatible
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB for app + space for vector database (scales with library size)
- **Internet**: Required for cloud LLM providers (optional if using Ollama)

## 🔧 Features

- ✅ **Chat with your library** - Ask questions, get cited answers
- ✅ **Semantic search** - Find papers by meaning, not just keywords
- ✅ **Evidence panel** - See exact passages used for each answer
- ✅ **Multiple LLM providers** - Ollama, OpenAI, Claude, and more
- ✅ **Profile system** - Multiple configurations for different projects
- ✅ **Advanced RAG** - BGE embeddings + BM25 + cross-encoder reranking
- ✅ **Session management** - Save and resume conversations
- ✅ **PDF integration** - Open papers directly from citations
- ✅ **Privacy-first** - Everything runs locally (except LLM API calls)

## ⚠️ Known Issues

- **Default icon**: Using placeholder Electron icon - custom icon coming in next release
- **Windows SmartScreen**: May show warning on first install (app is not yet code-signed)
- **Large libraries**: Initial indexing of 1000+ PDFs can take 30+ minutes
- **Beta software**: This is an early release - expect some rough edges

## 🆙 Upgrading from Web Version

Already using the web-based version?

- ✅ Your settings and profiles are preserved (`~/.zotero-llm/`)
- ✅ Your indexed library will be reused automatically
- ✅ No need to re-index unless you want to
- ✅ Can run both versions side-by-side

Simply install the desktop app and your existing data will be detected.

## 🔄 Auto-Updates

Once installed, the app will automatically:
- Check for updates on startup
- Notify you when updates are available
- Download updates in the background
- Prompt you to restart to apply updates

No need to visit GitHub for future versions!

## 📖 Documentation

- **Getting Started**: [Setup Guide](https://github.com/aahepburn/zotero-llm-plugin/blob/master/SETUP.md)
- **Desktop App Development**: [Desktop App Guide](https://github.com/aahepburn/zotero-llm-plugin/blob/master/docs/DESKTOP_APP.md)
- **Quick Reference**: [Command Cheat Sheet](https://github.com/aahepburn/zotero-llm-plugin/blob/master/QUICK_REFERENCE.md)
- **Full README**: [Project Overview](https://github.com/aahepburn/zotero-llm-plugin/blob/master/README.md)

## 🐛 Bug Reports & Feedback

Found a bug? Have suggestions?

- **Bug reports**: [Open an issue](https://github.com/aahepburn/zotero-llm-plugin/issues/new)
- **Feature requests**: [Start a discussion](https://github.com/aahepburn/zotero-llm-plugin/discussions)
- **Questions**: Check [existing discussions](https://github.com/aahepburn/zotero-llm-plugin/discussions) first

When reporting bugs, please include:
- Your OS and version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

## 🙏 Acknowledgments

This project builds on:
- [Zotero](https://www.zotero.org/) - The amazing reference manager
- [Ollama](https://ollama.ai/) - Easy local LLM deployment
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework
- [Electron](https://www.electronjs.org/) - Desktop app framework

## 📝 Changelog

See [CHANGELOG.md](https://github.com/aahepburn/zotero-llm-plugin/blob/master/CHANGELOG.md) for detailed changes.

### Technical Changes

- Implemented Electron desktop wrapper
- Added Python backend process management
- Implemented electron-updater for automatic updates
- Added IPC communication layer
- Created electron-builder configuration for all platforms
- Added GitHub Actions workflow for automated builds
- Enhanced backend with HEAD request support
- Added comprehensive documentation

## 🎯 What's Next?

Planned for future releases:

- 🎨 Custom app icon and branding
- 🔐 Code signing for macOS and Windows
- 📊 Better progress indicators for long operations
- 🌐 Additional LLM provider integrations
- 🔍 Enhanced search and filtering
- 📱 Native Zotero plugin (deep integration)
- 🗺️ Citation and influence graph visualization
- 📚 Book review discovery

## 💝 Support the Project

If you find this tool useful:
- ⭐ Star the repository
- 🐛 Report bugs and suggest features
- 📢 Share with other researchers
- 💬 Join the discussions

---

**First time using?** Check out the [Setup Guide](https://github.com/aahepburn/zotero-llm-plugin/blob/master/SETUP.md) to get started in 5 minutes!

**Developers?** See [Desktop App Guide](https://github.com/aahepburn/zotero-llm-plugin/blob/master/docs/DESKTOP_APP.md) to build from source or contribute.

Happy researching! 🎓✨
