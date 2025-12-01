# Setup Guide for New Machines

## Quick Setup (5 minutes)

```bash
# 1. Clone and navigate
git clone https://github.com/aahepburn/zotero-llm-plugin.git
cd zotero-llm-plugin

# 2. Run setup script
./setup.sh

# 3. Configure Zotero path
# Edit .env and set: ZOTERO_DB_PATH=/path/to/Zotero/zotero.sqlite

# 4. Start services
# Terminal 1:
source .venv/bin/activate
uvicorn backend.main:app --reload

# Terminal 2:
cd frontend && npm run dev

# 5. Open http://localhost:5173
# Configure API keys in Settings UI
```

## Common Zotero Database Locations

- **macOS**: `/Users/YOUR_USERNAME/Zotero/zotero.sqlite`
- **Windows**: `C:\Users\YOUR_USERNAME\Zotero\zotero.sqlite`
- **Linux**: `~/Zotero/zotero.sqlite`

## LLM Provider Options

### Ollama (Free, Local, Recommended)
```bash
# Install from https://ollama.ai
ollama serve

# Pull a model
ollama pull llama2
```
- No API key needed
- Runs locally
- Configure in Settings: base_url = `http://localhost:11434`

### Cloud Providers
Configure API keys in Settings UI:
- **OpenAI**: Get key from platform.openai.com
- **Anthropic**: Get key from console.anthropic.com
- **Others**: Perplexity, Google, Groq, OpenRouter

## Files You Need to Configure

1. **`.env`** (create from `.env.example`):
   - `ZOTERO_DB_PATH` - path to your Zotero database

2. **Settings UI** (after app starts):
   - LLM provider selection
   - API keys
   - Embedding model (default: bge-base)

## What Happens on First Run

The app automatically creates:
- `~/.zotero-llm/` directory
- Default profile with empty settings
- ChromaDB directory for vector storage

You need to:
1. Set Zotero database path
2. Choose LLM provider
3. Add API key (unless using Ollama)
4. Click "Index Library" to process PDFs

## Troubleshooting

### "Cannot find Zotero database"
- Check path in Settings or `.env`
- Make sure Zotero is installed
- Use absolute path, not `~/`

### "Ollama not responding"
```bash
# Make sure Ollama is running
ollama serve

# Check status
curl http://localhost:11434/api/tags
```

### "API key invalid"
- Double-check key in Settings UI
- Verify key has correct permissions
- Check for extra spaces/newlines

### "Nothing happens after indexing"
- Check Terminal 1 for backend logs
- Indexing can take time for large libraries
- Use "Index Status" button to check progress

## Need Help?

- See [SECURITY.md](SECURITY.md) for data/privacy info
- See [README.md](README.md) for full documentation
- Check [docs/](docs/) for technical details
- Open GitHub issue for bugs
