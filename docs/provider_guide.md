# LLM Provider System Guide

##  Overview

The Zotero RAG Assistant supports multiple LLM providers through a clean, provider-agnostic architecture:

- **Ollama** (Local, free)
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude)
- **Mistral** (Mistral Large, Mixtral)
- **Google** (Gemini)
- **Groq** (Fast Llama)
- **OpenRouter** (Unified access)

##  Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Backend

```bash
uvicorn backend.main:app --reload
```

### 3. Configure via UI

1. Open Settings page
2. Enable desired providers
3. Add API keys
4. Test connections
5. Select active provider/model
6. Save and start chatting!

##  What Was Implemented

### Backend (Python)

```
backend/model_providers/
 base.py              # Provider protocol/interface
 ollama.py            # Local Ollama support
 openai.py            # OpenAI GPT models
 anthropic.py         # Anthropic Claude
 additional.py        # Mistral, Google, Groq, OpenRouter
 __init__.py          # Provider registry & manager
```

**Updated Files:**
- `main.py` - New endpoints & settings system
- `interface.py` - Uses ProviderManager
- `requirements.txt` - Added openai, anthropic, google-generativeai

### Frontend (TypeScript/React)

**Updated Files:**
- `contexts/SettingsContext.tsx` - New provider types
- `pages/Settings.tsx` - Complete rewrite with provider UI
- `styles/settings.css` - Provider card styles

### Documentation

- `docs/multi_provider_system.md` - Complete documentation
- `docs/PROVIDER_QUICKSTART.md` - This file

##  Getting API Keys

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and paste into Settings

### Anthropic
1. Go to https://console.anthropic.com/account/keys
2. Create new API key
3. Copy and paste into Settings

### Google (Gemini)
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Copy and paste into Settings

### Others
- **Mistral**: https://console.mistral.ai/api-keys/
- **Groq**: https://console.groq.com/keys
- **OpenRouter**: https://openrouter.ai/keys

##  New API Endpoints

```
GET  /providers                    # List all providers
GET  /providers/{id}/models        # Get models for provider
POST /providers/{id}/validate      # Test credentials
GET  /providers/{id}/status        # Check availability
GET  /settings                     # Get settings (new format)
POST /settings                     # Save settings (auto-migrates old format)
```

##  Usage Examples

### Via Settings UI (Easiest)

1. Settings → Enable "Anthropic"
2. Enter API key
3. Test Connection
4. Set as active provider
5. Choose "Claude 3.5 Sonnet"
6. Save → Done!

### Programmatically

```python
from backend.model_providers import ProviderManager, Message

manager = ProviderManager(
    active_provider_id="anthropic",
    credentials={"anthropic": {"api_key": "sk-ant-..."}}
)

response = manager.chat([
    Message(role="user", content="What is quantum computing?")
])

print(response.content)
```

##  Security

-  API keys masked in UI
-  Stored locally in `~/.zotero-llm/settings.json`
-  Never logged or exposed
-  Per-provider validation

##  Features

### Provider Management
- Enable/disable any provider
- Multiple providers enabled simultaneously
- Switch active provider anytime

### Model Selection
- Dynamic model loading per provider
- Use default or choose specific model
- See model descriptions and context lengths

### Connection Testing
- Test before saving
- Clear error messages
- Status indicators

### Settings Migration
- Old format auto-migrates
- No data loss
- Backward compatible

##  Troubleshooting

### Ollama not connecting
```bash
# Make sure Ollama is running
ollama serve

# Pull a model if needed
ollama pull llama3.2
```

### Invalid API key
- Check format (OpenAI: `sk-...`, Anthropic: `sk-ant-...`)
- Verify key is active in provider dashboard
- Test connection in Settings

### Model not found
- For Ollama: Pull model first
- For cloud providers: Check model name is current

##  Documentation

- **Full docs**: `docs/multi_provider_system.md`
- **Architecture details**: See `backend/model_providers/base.py`
- **API reference**: See full docs for all endpoints

##  Benefits

1. **Flexibility** - Switch providers without code changes
2. **Privacy** - Use local Ollama for sensitive data
3. **Cost** - Mix free and paid options
4. **Quality** - Choose best model for each task
5. **Future-proof** - Easy to add new providers

##  Status

 **Production Ready**

All features implemented and tested:
- [x] 7 provider integrations
- [x] Settings UI with provider management
- [x] API endpoints for provider operations
- [x] Automatic settings migration
- [x] Secure credential handling
- [x] Documentation complete

##  Next Steps (Optional)

Potential enhancements:
- Streaming responses
- Cost tracking
- Model comparison
- Response caching
- Rate limit handling

See `docs/multi_provider_system.md` for details.

---

**Questions?** Check the full documentation in `docs/multi_provider_system.md`
