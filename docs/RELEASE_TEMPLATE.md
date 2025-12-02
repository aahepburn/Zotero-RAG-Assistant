# Release Template

Use this template when creating a new GitHub Release.

---

## 🎉 Zotero LLM Assistant v0.1.0 - Desktop App

A native desktop application that brings AI-powered chat to your Zotero library. Chat with your research, get cited answers, and search semantically across all your PDFs.

### ✨ What's New

- 🖥️ **Native desktop app** for macOS, Windows, and Linux
- 🔄 **Automatic updates** - future versions install automatically
- 🐍 **No setup required** - Python and all dependencies bundled
- ⚡ **Improved performance** with native integrations
- 🎨 **Better UI** with native window chrome

### 📥 Installation

Download the installer for your platform:

| Platform | Download | Notes |
|----------|----------|-------|
| **macOS** | [Zotero-LLM-Assistant-0.1.0-mac.dmg](#) | Universal (Intel + Apple Silicon) |
| **Windows** | [Zotero-LLM-Assistant-0.1.0-win.exe](#) | Windows 10/11, 64-bit |
| **Linux** | [Zotero-LLM-Assistant-0.1.0-linux.AppImage](#) | Ubuntu 20.04+, or use .deb |

**First time setup:**
1. Install the app
2. Launch and set your Zotero database path in Settings
3. Configure your LLM provider (Ollama, OpenAI, Claude, etc.)
4. Click "Index Library" to process your PDFs
5. Start chatting with your research! 🚀

### 🔧 System Requirements

- **macOS**: 10.13 (High Sierra) or later
- **Windows**: Windows 10 or later
- **Linux**: Ubuntu 20.04+, Debian 10+, or compatible
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB for app + space for vector database

### ⚠️ Known Issues

- This is a beta release - expect some rough edges
- Large libraries (1000+ PDFs) may take time to index
- Windows users may see SmartScreen warning (click "More info" → "Run anyway")

### 🆙 Upgrading from Web Version

If you were using the web version (running manually with `npm run dev`):
- Your settings and profiles are preserved in `~/.zotero-llm/`
- Your indexed library will be reused automatically
- No need to re-index unless you want to

### 📖 Documentation

- [Desktop App Guide](https://github.com/aahepburn/zotero-llm-plugin/blob/master/docs/DESKTOP_APP.md)
- [Setup Guide](https://github.com/aahepburn/zotero-llm-plugin/blob/master/SETUP.md)
- [Quick Reference](https://github.com/aahepburn/zotero-llm-plugin/blob/master/QUICK_REFERENCE.md)

### 🐛 Bug Reports

Found a bug? [Open an issue](https://github.com/aahepburn/zotero-llm-plugin/issues/new) with:
- Your OS and version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

### 💬 Feedback

We'd love to hear from you! Share your experience in [Discussions](https://github.com/aahepburn/zotero-llm-plugin/discussions).

### 📝 Full Changelog

See [CHANGELOG.md](https://github.com/aahepburn/zotero-llm-plugin/blob/master/CHANGELOG.md) for complete changes.

---

**Auto-updates:** Installed apps will automatically check for and install future updates. No need to manually download new versions!
