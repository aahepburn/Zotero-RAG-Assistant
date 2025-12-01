"""
OpenAI provider for GPT models.

Implements the ModelProvider interface for OpenAI's API, supporting
GPT-4, GPT-3.5, and other OpenAI models.
"""

from typing import Dict, Any, List, Optional
from .base import (
    BaseProvider, Message, ChatResponse, ModelInfo,
    ProviderError, ProviderAuthenticationError, ProviderConnectionError
)


class OpenAIProvider(BaseProvider):
    """Provider implementation for OpenAI models."""
    
    def __init__(self):
        super().__init__(
            id="openai",
            label="OpenAI",
            default_model="gpt-4o-mini",
            supports_streaming=True,
            requires_api_key=True,
        )
        self._client = None
    
    def _get_client(self, credentials: Dict[str, Any]):
        """Get or create OpenAI client with credentials."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ProviderError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
        api_key = credentials.get("api_key")
        if not api_key:
            raise ProviderAuthenticationError("OpenAI API key is required")
        
        base_url = credentials.get("base_url")  # For custom endpoints
        return OpenAI(api_key=api_key, base_url=base_url)
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate OpenAI API key by making a test request."""
        try:
            client = self._get_client(credentials)
            # Try to list models as a validation check
            client.models.list()
            return True
        except ImportError as e:
            raise ProviderError(str(e))
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                raise ProviderAuthenticationError(f"Invalid OpenAI API key: {str(e)}")
            elif "connection" in error_msg or "network" in error_msg:
                raise ProviderConnectionError(f"Cannot connect to OpenAI: {str(e)}")
            else:
                raise ProviderError(f"OpenAI validation failed: {str(e)}")
    
    def list_models(self, credentials: Dict[str, Any]) -> List[ModelInfo]:
        """
        List available OpenAI models.
        
        Returns a curated list of useful models rather than the full API response.
        """
        try:
            client = self._get_client(credentials)
            # Get models from API
            models_response = client.models.list()
            
            # Define curated models we care about for academic use
            curated_models = {
                "gpt-4o": ModelInfo(
                    id="gpt-4o",
                    name="GPT-4o",
                    description="Most capable model, best for complex reasoning",
                    context_length=128000
                ),
                "gpt-4o-mini": ModelInfo(
                    id="gpt-4o-mini",
                    name="GPT-4o Mini",
                    description="Fast and affordable, good for most tasks",
                    context_length=128000
                ),
                "gpt-4-turbo": ModelInfo(
                    id="gpt-4-turbo",
                    name="GPT-4 Turbo",
                    description="Previous generation flagship model",
                    context_length=128000
                ),
                "gpt-3.5-turbo": ModelInfo(
                    id="gpt-3.5-turbo",
                    name="GPT-3.5 Turbo",
                    description="Fast and economical",
                    context_length=16385
                ),
            }
            
            # Filter to only include models that actually exist in the account
            available_model_ids = {model.id for model in models_response.data}
            available_models = [
                info for model_id, info in curated_models.items()
                if model_id in available_model_ids or model_id.startswith("gpt-")
            ]
            
            # If we found any of our curated models, return those
            # Otherwise, return all GPT models from the API
            if available_models:
                return available_models
            else:
                # Fallback: return all gpt models
                return [
                    ModelInfo(
                        id=model.id,
                        name=model.id,
                        description=None,
                        context_length=None
                    )
                    for model in models_response.data
                    if "gpt" in model.id.lower()
                ]
                
        except Exception as e:
            raise ProviderError(f"Failed to list OpenAI models: {str(e)}")
    
    def chat(
        self,
        credentials: Dict[str, Any],
        model: str,
        messages: List[Message],
        temperature: float = 0.3,
        max_tokens: int = 512,
        **kwargs
    ) -> ChatResponse:
        """Generate a chat completion using OpenAI."""
        try:
            client = self._get_client(credentials)
            
            # Convert to OpenAI message format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Make the API call
            response = client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )
            
            # Extract response
            content = response.choices[0].message.content or ""
            
            # Parse usage
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            return ChatResponse(
                content=content,
                model=response.model,
                usage=usage,
                raw=response.model_dump() if hasattr(response, 'model_dump') else None
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg:
                raise ProviderAuthenticationError(f"OpenAI authentication failed: {str(e)}")
            elif "rate limit" in error_msg:
                raise ProviderError(f"OpenAI rate limit exceeded: {str(e)}")
            elif "context length" in error_msg or "maximum context" in error_msg:
                raise ProviderError(f"Context too long for model {model}: {str(e)}")
            else:
                raise ProviderError(f"OpenAI chat failed: {str(e)}")
