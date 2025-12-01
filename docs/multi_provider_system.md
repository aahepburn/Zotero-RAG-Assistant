# Multi-Provider LLM System

## Overview

The Zotero LLM Plugin now supports multiple LLM providers through a clean, provider-agnostic architecture. Users can easily switch between local models (Ollama) and cloud APIs (OpenAI, Anthropic, Perplexity, Google, Groq, OpenRouter).

## Architecture

### Backend Components

#### 1. Provider Interface (`backend/model_providers/base.py`)

Defines the `ModelProvider` protocol that all providers must implement:

```python
class ModelProvider(Protocol):
    @property
    def id(self) -> str: ...
    
    @property
    def label(self) -> str: ...
    
    def validate_credentials(self, credentials: Dict) -> bool: ...
    
    def list_models(self, credentials: Dict) -> List[ModelInfo]: ...
    
    def chat(
        self, 
        credentials: Dict, 
        model: str, 
        messages: List[Message],
        **kwargs
    ) -> ChatResponse: ...
```

#### 2. Provider Implementations

Each provider adapter lives in its own file:

- **`ollama.py`** - Local Ollama models (no API key required)
- **`openai.py`** - OpenAI GPT models
- **`anthropic.py`** - Anthropic Claude models
- **`additional.py`** - Perplexity, Google Gemini, Groq, OpenRouter

All providers inherit from `BaseProvider` and implement the `ModelProvider` protocol.

#### 3. Provider Registry (`backend/model_providers/__init__.py`)

Central registry managing all providers:

```python
from backend.model_providers import (
    ProviderManager,
    get_provider,
    list_providers,
    get_provider_info
)

# Get all providers
providers = list_providers()

# Get specific provider
ollama = get_provider("ollama")

# High-level manager
manager = ProviderManager(
    active_provider_id="anthropic",
    active_model="claude-3-5-sonnet-20241022",
    credentials={"anthropic": {"api_key": "sk-..."}}
)

response = manager.chat([Message(role="user", content="Hello")])
```

#### 4. Updated Backend (`main.py` & `interface.py`)

- **Settings system** - Refactored to support per-provider credentials
- **ZoteroChatbot** - Now uses `ProviderManager` instead of hardcoded Ollama
- **New endpoints**:
  - `GET /providers` - List all available providers
  - `GET /providers/{id}/models` - List models for a provider
  - `POST /providers/{id}/validate` - Validate credentials
  - `GET /providers/{id}/status` - Check provider availability

### Frontend Components

#### 1. Updated Types (`SettingsContext.tsx`)

```typescript
interface ProviderConfig {
  enabled: boolean;
  credentials: ProviderCredentials;
}

interface Settings {
  activeProviderId: string;    // Currently active provider
  activeModel: string;          // Currently active model
  providers: Record<string, ProviderConfig>;
}
```

#### 2. Enhanced Settings UI (`Settings.tsx`)

New features:
- **Provider selection** - Choose active provider from dropdown
- **Model selection** - Select specific model or use default
- **Per-provider configuration** - Enable/disable and configure each provider
- **Credential management** - Secure API key input with masking
- **Connection testing** - Test credentials before saving
- **Model loading** - Dynamically load available models per provider

## Supported Providers

### 1. Ollama (Local)
- **ID**: `ollama`
- **Requires API Key**: No
- **Configuration**: Base URL (default: `http://localhost:11434`)
- **Models**: Llama, Mistral, and any model you've pulled locally
- **Best for**: Privacy, offline use, no cost

### 2. OpenAI
- **ID**: `openai`
- **Requires API Key**: Yes
- **Models**: GPT-4o, GPT-4o Mini, GPT-4 Turbo, GPT-3.5 Turbo
- **Best for**: Highest quality responses, cutting-edge capabilities

### 3. Anthropic
- **ID**: `anthropic`
- **Requires API Key**: Yes
- **Models**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- **Best for**: Long context, careful reasoning, safety

### 4. Perplexity
- **ID**: `perplexity`
- **Requires API Key**: Yes
- **Models**: Sonar, Sonar Pro
- **Best for**: Research queries with web search integration

### 5. Google
- **ID**: `google`
- **Requires API Key**: Yes
- **Models**: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0 Flash
- **Best for**: Extremely long context (up to 2M tokens)

### 6. Groq
- **ID**: `groq`
- **Requires API Key**: Yes
- **Models**: Llama 3.3 70B, Llama 3.1 8B
- **Best for**: Very fast inference, open models

### 7. OpenRouter
- **ID**: `openrouter`
- **Requires API Key**: Yes
- **Models**: Access to many models through unified API
- **Best for**: Flexibility, comparing different models

## Settings Storage

Settings are stored in `~/.zotero-llm/settings.json`:

```json
{
  "activeProviderId": "ollama",
  "activeModel": "",
  "zoteroPath": "/Users/username/Zotero/zotero.sqlite",
  "chromaPath": "/Users/username/.zotero-llm/chroma/user-1",
  "providers": {
    "ollama": {
      "enabled": true,
      "credentials": {
        "base_url": "http://localhost:11434"
      }
    },
    "openai": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    },
    "anthropic": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    }
  }
}
```

### Security

- API keys are masked in the frontend UI (shown as `***`)
- Credentials are stored locally in `~/.zotero-llm/`
- API keys are never logged or exposed in error messages
- Each provider validates credentials separately

## Migration from Old System

The system automatically migrates old settings format:

**Old format:**
```json
{
  "openaiApiKey": "sk-...",
  "anthropicApiKey": "sk-ant-...",
  "defaultModel": "gpt-4"
}
```

**Automatically converted to:**
```json
{
  "activeProviderId": "openai",
  "activeModel": "gpt-4",
  "providers": {
    "openai": {
      "enabled": true,
      "credentials": {"api_key": "sk-..."}
    },
    "anthropic": {
      "enabled": true,
      "credentials": {"api_key": "sk-ant-..."}
    }
  }
}
```

## Usage Examples

### Backend

```python
# Initialize chatbot with provider settings
from backend.interface import ZoteroChatbot

chatbot = ZoteroChatbot(
    db_path="path/to/zotero.sqlite",
    chroma_path="path/to/chroma",
    active_provider_id="anthropic",
    active_model="claude-3-5-sonnet-20241022",
    credentials={
        "anthropic": {"api_key": "sk-ant-..."}
    }
)

# Chat uses the configured provider
response = chatbot.chat("What are the main findings?")
```

### Switching Providers Programmatically

```python
# Update provider settings dynamically
chatbot.update_provider_settings(
    active_provider_id="openai",
    active_model="gpt-4o",
    credentials={
        "openai": {"api_key": "sk-..."}
    }
)
```

### Direct Provider Usage

```python
from backend.model_providers import get_provider, Message

provider = get_provider("anthropic")
messages = [Message(role="user", content="Hello!")]
response = provider.chat(
    credentials={"api_key": "sk-ant-..."},
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    temperature=0.7
)

print(response.content)
```

## Adding New Providers

To add a new provider:

1. **Create provider file** (e.g., `backend/model_providers/cohere.py`):

```python
from .base import BaseProvider, Message, ChatResponse, ModelInfo

class CohereProvider(BaseProvider):
    def __init__(self):
        super().__init__(
            id="cohere",
            label="Cohere",
            default_model="command-r-plus",
            requires_api_key=True
        )
    
    def validate_credentials(self, credentials):
        # Implement validation
        pass
    
    def list_models(self, credentials):
        # Return available models
        pass
    
    def chat(self, credentials, model, messages, **kwargs):
        # Implement chat completion
        pass
```

2. **Register in `__init__.py`**:

```python
from .cohere import CohereProvider

def _initialize_providers():
    providers = [
        # ... existing providers
        CohereProvider(),
    ]
    for provider in providers:
        register_provider(provider)
```

3. **Add to default settings** in `main.py`:

```python
"providers": {
    # ... existing providers
    "cohere": {
        "enabled": False,
        "credentials": {"api_key": ""}
    }
}
```

4. **Update frontend types** in `SettingsContext.tsx` to include the new provider.

## API Reference

### Provider Endpoints

#### `GET /providers`
List all available providers.

**Response:**
```json
{
  "providers": [
    {
      "id": "ollama",
      "label": "Ollama (Local)",
      "default_model": "llama3.2",
      "supports_streaming": true,
      "requires_api_key": false
    }
  ]
}
```

#### `GET /providers/{provider_id}/models`
List models for a provider.

**Response:**
```json
{
  "models": [
    {
      "id": "gpt-4o",
      "name": "GPT-4o",
      "description": "Most capable model",
      "context_length": 128000
    }
  ]
}
```

#### `POST /providers/{provider_id}/validate`
Validate provider credentials.

**Request:**
```json
{
  "credentials": {
    "api_key": "sk-..."
  }
}
```

**Response:**
```json
{
  "valid": true,
  "provider": "openai"
}
```

#### `GET /providers/{provider_id}/status`
Check provider status.

**Response:**
```json
{
  "status": "available",
  "provider": "ollama",
  "label": "Ollama (Local)"
}
```

## Dependencies

New dependencies added to `requirements.txt`:

```
openai>=1.0.0
anthropic>=0.18.0
google-generativeai>=0.3.0
```

Install with:
```bash
pip install -r requirements.txt
```

## Benefits

1. **User Choice** - Switch between local and cloud models based on needs
2. **Extensibility** - Easy to add new providers without changing core code
3. **Clean Architecture** - Provider-agnostic interface ensures consistency
4. **Security** - Proper credential management and validation
5. **Flexibility** - Per-session provider/model overrides possible
6. **Cost Control** - Use free local models or pay-per-use cloud APIs
7. **Privacy** - Option to keep all data local with Ollama

## Future Enhancements

Potential improvements:

- **Streaming support** - Real-time response streaming for long answers
- **Cost tracking** - Monitor API usage and costs per provider
- **Model comparison** - A/B test different models on same queries
- **Caching** - Cache responses to reduce API calls
- **Rate limiting** - Built-in rate limit handling per provider
- **Fallback chains** - Auto-fallback to alternative provider if primary fails
- **Custom endpoints** - Support for self-hosted API endpoints
