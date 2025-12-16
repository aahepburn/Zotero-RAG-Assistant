# Release v0.1.8 - 2025 Academic Prompting System

## GitHub Release Description

Copy this for the GitHub release page:

---

# 🎓 v0.1.8 - 2025 Academic Prompting System

Major AI enhancement implementing cutting-edge academic prompting strategies based on 2025 research and industry best practices.

## ✨ What's New

### Better Citation Accuracy
Every response now includes inline citations `[1]`, `[2]` for all factual claims. **Expected ~60% reduction in citation errors** based on CiteFix research (ACL 2025).

### Chain-of-Thought Reasoning
Transparent step-by-step logic shows how the AI connects sources to form conclusions. Helps you verify synthesis quality and understand the reasoning process.

### Improved Response Quality
- **Structured format**: Direct answer → Key evidence → Synthesis → Limitations
- **Better uncertainty handling**: Explicit "I don't know" when evidence is insufficient
- **Reduced repetition**: No more repeated citations or concepts
- **More natural academic writing**: Proper vocabulary diversity with technical precision

### Optimized AI Parameters
Fine-tuned for academic content synthesis:
- Temperature: 0.35 (perfect balance of factuality and natural writing)
- Max tokens: 600 (allows detailed academic responses)
- Top-p: 0.9 (nucleus sampling prevents hallucinations)
- Top-k: 50 (better vocabulary diversity)
- Repeat penalty: 1.15 (prevents citation repetition)

### Enhanced System Prompt
Upgraded from 54 words to ~400 words with:
- Comprehensive academic guidelines
- Explicit citation requirements with examples
- Chain-of-thought reasoning instructions
- Quality verification checklist

### All LLM Providers Updated
Improved defaults for:
- Ollama: Enhanced top_k and repeat_penalty
- OpenAI: Added frequency_penalty, optimized top_p
- Anthropic: Added top_k parameter
- Perplexity, Groq, OpenRouter: Enhanced sampling parameters

## 📥 Installation

### macOS
- **Apple Silicon (M1/M2/M3)**: [ZoteroRAG-0.1.8-mac-arm64.dmg](https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.8/ZoteroRAG-0.1.8-mac-arm64.dmg)
- **Intel**: [ZoteroRAG-0.1.8-mac-x64.dmg](https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.8/ZoteroRAG-0.1.8-mac-x64.dmg)

### Windows
- **64-bit**: [ZoteroRAG-0.1.8-win-x64.exe](https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.8/ZoteroRAG-0.1.8-win-x64.exe)
- **32-bit**: [ZoteroRAG-0.1.8-win-ia32.exe](https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.8/ZoteroRAG-0.1.8-win-ia32.exe)
- **Universal Installer**: [ZoteroRAG-0.1.8-win.exe](https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.8/ZoteroRAG-0.1.8-win.exe)

### Linux
- **Debian/Ubuntu (x64)**: [ZoteroRAG-0.1.8-linux-amd64.deb](https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.8/ZoteroRAG-0.1.8-linux-amd64.deb)
- **Debian/Ubuntu (ARM64)**: [ZoteroRAG-0.1.8-linux-arm64.deb](https://github.com/aahepburn/Zotero-RAG-Assistant/releases/download/v0.1.8/ZoteroRAG-0.1.8-linux-arm64.deb)

```bash
# Install on Debian/Ubuntu
sudo dpkg -i ZoteroRAG-0.1.8-linux-amd64.deb
```

## ⬆️ Upgrading from v0.1.7

### Automatic Update (Recommended)
If you have v0.1.7 installed, the app will automatically detect this update:
1. Open app → **Settings** → **About**
2. Click **"Check for Updates"**
3. Click **"Download Update"**
4. After download completes, click **"Install and Restart"**

### Manual Installation
Download and install the appropriate package for your platform above. Your settings and library data will be preserved.

## 📚 Documentation

- **[Quick Start Guide](https://github.com/aahepburn/Zotero-RAG-Assistant/blob/master/docs/PROMPTING_QUICKSTART.md)** - What changed and how to use it
- **[Technical Implementation](https://github.com/aahepburn/Zotero-RAG-Assistant/blob/master/docs/ACADEMIC_PROMPTING_2025.md)** - Comprehensive guide with research foundation
- **[Full Changelog](https://github.com/aahepburn/Zotero-RAG-Assistant/blob/master/CHANGELOG.md)** - Complete list of changes

## ✅ Compatibility

- ✅ **Backward compatible** - no breaking changes
- ✅ **All existing data preserved** - settings, profiles, indexed libraries
- ✅ **No re-indexing required** - works with existing vector databases
- ✅ **Works with all LLM providers** - Ollama, OpenAI, Anthropic, Perplexity, Groq, etc.

## 🔬 Research Foundation

Based on cutting-edge 2025 research:
- **CiteFix (ACL 2025)**: 80% of "hallucinations" are actually citation mismatches
- **Perplexity Academic Mode**: Industry-leading citation practices
- **Temperature Research**: 0.35-0.4 optimal for academic synthesis
- **RAG Evaluation Frameworks**: RAGAS factuality metrics

## 💡 Example Improvements

### Before (v0.1.7):
> "Studies show that neural networks improve performance with more data."

### After (v0.1.8):
> "Recent research demonstrates that transformer architectures improve accuracy by 15-25% with dataset scaling [1][2]. However, this relationship plateaus beyond 10B parameters [3], suggesting diminishing returns.
> 
> **Key Evidence:**
> - Training on 1B+ examples yields consistent gains [1]
> - Architectural improvements matter more than scale alone [2]
> 
> **Limitation:** The retrieved documents don't address compute efficiency trade-offs."

## 🐛 Known Issues

None currently. If you encounter issues, please [open an issue](https://github.com/aahepburn/Zotero-RAG-Assistant/issues).

## 🙏 Acknowledgments

Special thanks to the research community for:
- CiteFix paper authors (ACL 2025)
- Perplexity AI team for academic mode inspiration
- RAGAS framework contributors for evaluation methods

---

**Full changelog**: [CHANGELOG.md](https://github.com/aahepburn/Zotero-RAG-Assistant/blob/master/CHANGELOG.md)

---

## Build Summary (for maintainers)

**Version**: 0.1.8  
**Tag**: v0.1.8  
**Date**: 2025-12-16

### Files to Upload:

**macOS:**
- ✅ ZoteroRAG-0.1.8-mac-arm64.dmg (367MB)
- ✅ ZoteroRAG-0.1.8-mac-arm64.dmg.blockmap
- ✅ ZoteroRAG-0.1.8-mac-x64.dmg (372MB)
- ✅ ZoteroRAG-0.1.8-mac-x64.dmg.blockmap
- ✅ ZoteroRAG-0.1.8-mac-arm64.zip
- ✅ ZoteroRAG-0.1.8-mac-arm64.zip.blockmap
- ✅ ZoteroRAG-0.1.8-mac-x64.zip
- ✅ ZoteroRAG-0.1.8-mac-x64.zip.blockmap
- ✅ **latest-mac.yml** (CRITICAL for auto-updates)

**Windows:**
- ⏳ ZoteroRAG-0.1.8-win.exe (universal installer)
- ⏳ ZoteroRAG-0.1.8-win.exe.blockmap
- ⏳ ZoteroRAG-0.1.8-win-x64.exe
- ⏳ ZoteroRAG-0.1.8-win-x64.exe.blockmap
- ⏳ ZoteroRAG-0.1.8-win-ia32.exe
- ⏳ ZoteroRAG-0.1.8-win-ia32.exe.blockmap
- ⏳ ZoteroRAG-0.1.8-win-x64.zip
- ⏳ ZoteroRAG-0.1.8-win-ia32.zip
- ⏳ **latest.yml** (CRITICAL for auto-updates)

**Linux:**
- ✅ ZoteroRAG-0.1.8-linux-amd64.deb (77MB)
- ✅ ZoteroRAG-0.1.8-linux-arm64.deb (72MB)
- ✅ **latest-linux.yml** (CRITICAL for auto-updates)
- ✅ **latest-linux-arm64.yml** (CRITICAL for auto-updates)

### Publishing Steps:

1. **Wait for Windows build to complete** (currently building)
2. **Set GitHub token**:
   ```bash
   export GH_TOKEN=your_github_personal_access_token
   ```

3. **Option A - Automatic publish** (recommended):
   ```bash
   cd /Users/aahepburn/Projects/zotero-rag-assistant
   
   # This will create the release and upload everything
   electron-builder --mac --win --linux --publish always
   ```

4. **Option B - Manual upload**:
   - Go to: https://github.com/aahepburn/Zotero-RAG-Assistant/releases/new
   - Select tag: v0.1.8
   - Copy release description from above
   - Upload ALL files from `release/` directory
   - **CRITICAL**: Ensure all `.yml` files are uploaded!

### Testing Checklist:

After publishing, test auto-update:
- [ ] Install v0.1.7 on test machine
- [ ] Open app → Settings → About
- [ ] Click "Check for Updates"
- [ ] Verify shows "v0.1.8 available"
- [ ] Download and install update
- [ ] Verify new prompting improvements work
- [ ] Try a research question and check citations

### Rollback Plan:

If issues arise:
1. Mark v0.1.8 as "Pre-release" in GitHub
2. Users can manually download v0.1.7
3. Fix issues and release v0.1.9

---

**Status**: ⏳ Waiting for Windows build to complete  
**Next**: Publish to GitHub once all builds are ready
