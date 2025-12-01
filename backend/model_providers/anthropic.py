"""
Anthropic provider for Claude models.

Implements the ModelProvider interface for Anthropic's API, supporting
Claude 3 family of models.
"""

from typing import Dict, Any, List
from .base import (
    BaseProvider, Message, ChatResponse, ModelInfo,
    ProviderError, ProviderAuthenticationError, ProviderConnectionError
)


class AnthropicProvider(BaseProvider):
    """Provider implementation for Anthropic Claude models."""
    
    def __init__(self):
        super().__init__(
            id="anthropic",
            label="Anthropic",
            default_model="claude-3-5-sonnet-20241022",
            supports_streaming=True,
            requires_api_key=True,
        )
    
    def _get_client(self, credentials: Dict[str, Any]):
        """Get or create Anthropic client with credentials."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ProviderError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
        
        api_key = credentials.get("api_key")
        if not api_key:
            raise ProviderAuthenticationError("Anthropic API key is required")
        
        return Anthropic(api_key=api_key)
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Anthropic API key by making a test request."""
        try:
            client = self._get_client(credentials)
            # Make a minimal request to test the API key
            # Anthropic doesn't have a models list endpoint, so we make a tiny chat request
            client.messages.create(
                model=self.default_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except ImportError as e:
            raise ProviderError(str(e))
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                raise ProviderAuthenticationError(f"Invalid Anthropic API key: {str(e)}")
            elif "connection" in error_msg or "network" in error_msg:
                raise ProviderConnectionError(f"Cannot connect to Anthropic: {str(e)}")
            else:
                raise ProviderError(f"Anthropic validation failed: {str(e)}")
    
    def list_models(self, credentials: Dict[str, Any]) -> List[ModelInfo]:
        """
        List available Anthropic models.
        
        Anthropic doesn't provide a models API, so we return a curated list.
        """
        return [
            ModelInfo(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                description="Most intelligent model, best for complex reasoning",
                context_length=200000
            ),
            ModelInfo(
                id="claude-3-5-haiku-20241022",
                name="Claude 3.5 Haiku",
                description="Fastest model, good for simple tasks",
                context_length=200000
            ),
            ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                description="Previous flagship model, highly capable",
                context_length=200000
            ),
            ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                description="Balanced performance and speed",
                context_length=200000
            ),
            ModelInfo(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                description="Fast and efficient",
                context_length=200000
            ),
        ]
    
    def chat(
        self,
        credentials: Dict[str, Any],
        model: str,
        messages: List[Message],
        temperature: float = 0.3,
        max_tokens: int = 512,
        **kwargs
    ) -> ChatResponse:
        """Generate a chat completion using Anthropic Claude."""
        try:
            client = self._get_client(credentials)
            
            # Anthropic requires system messages to be separate
            system_message = None
            conversation_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    conversation_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Ensure we have at least one user message
            if not conversation_messages:
                raise ProviderError("At least one non-system message is required")
            
            # Make the API call
            request_params = {
                "model": model,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": kwargs.get("top_p", 1.0),
            }
            
            if system_message:
                request_params["system"] = system_message
            
            response = client.messages.create(**request_params)
            
            # Extract response content
            content = ""
            if response.content:
                # Claude returns content as a list of blocks
                content = " ".join(
                    block.text for block in response.content 
                    if hasattr(block, 'text')
                )
            
            # Parse usage
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
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
                raise ProviderAuthenticationError(f"Anthropic authentication failed: {str(e)}")
            elif "rate limit" in error_msg:
                raise ProviderError(f"Anthropic rate limit exceeded: {str(e)}")
            elif "context" in error_msg or "maximum" in error_msg:
                raise ProviderError(f"Context too long for model {model}: {str(e)}")
            else:
                raise ProviderError(f"Anthropic chat failed: {str(e)}")
