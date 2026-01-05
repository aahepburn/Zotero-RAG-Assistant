# backend/local_llm.py
# 
# DEPRECATED: This file is no longer used in the codebase.
# 
# This module has been superseded by backend/model_providers/ which provides:
# - Multi-provider support (Ollama, OpenAI, Anthropic, Perplexity)
# - Unified Message-based interface for conversational RAG
# - Better parameter management via AcademicGenerationParams
# - Support for proper conversation structure (system/user/assistant roles)
#
# See: backend/model_providers/__init__.py for the current implementation
#
# This file is retained for reference only and should not be imported.
# TODO: Remove this file in a future cleanup.

from typing import Optional
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # change if you use a different local model

def generate_answer(prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> str:
    """Generate answer with optimized parameters for academic RAG.
    
    DEPRECATED: Use backend.model_providers.ProviderManager.chat() instead.
    
    This function uses the old Ollama /api/generate endpoint with a simple prompt string.
    The new system uses /api/chat with structured messages (system/user/assistant) which
    is required for proper conversational RAG with multi-turn conversations.
    
    Best practices:
    - max_tokens: 400-600 for detailed academic answers
    - temperature: 0.2-0.4 (low for factual accuracy, not too low to avoid repetition)
    - top_p: 0.9 for nucleus sampling (better than pure temperature)
    """
    raise DeprecationWarning(
        "generate_answer() is deprecated. Use ProviderManager.chat() instead.\n"
        "Example:\n"
        "  from backend.model_providers import ProviderManager, Message\n"
        "  provider = ProviderManager(active_provider_id='ollama')\n"
        "  response = provider.chat(messages=[Message(role='user', content=prompt)])\n"
    )
    return (data.get("response") or "").strip()
