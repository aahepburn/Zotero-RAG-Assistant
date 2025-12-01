"""
Additional LLM providers: Perplexity, Google, Mistral, Groq, and OpenRouter.

These providers use OpenAI-compatible APIs or their own SDKs.
"""

from typing import Dict, Any, List
from .base import (
    BaseProvider, Message, ChatResponse, ModelInfo,
    ProviderError, ProviderAuthenticationError, ProviderConnectionError
)


class PerplexityProvider(BaseProvider):
    """
    Provider for Perplexity AI (Sonar models).
    Uses OpenAI-compatible API.
    """
    
    def __init__(self):
        super().__init__(
            id="perplexity",
            label="Perplexity",
            default_model="sonar",
            supports_streaming=True,
            requires_api_key=True,
        )
    
    def _get_client(self, credentials: Dict[str, Any]):
        """Get OpenAI-compatible client for Perplexity."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ProviderError(
                "OpenAI package required for Perplexity. Install with: pip install openai"
            )
        
        api_key = credentials.get("api_key")
        if not api_key:
            raise ProviderAuthenticationError("Perplexity API key is required")
        
        return OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Perplexity API key."""
        try:
            client = self._get_client(credentials)
            # Test with a minimal request
            client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                raise ProviderAuthenticationError(f"Invalid Perplexity API key: {str(e)}")
            raise ProviderError(f"Perplexity validation failed: {str(e)}")
    
    def list_models(self, credentials: Dict[str, Any]) -> List[ModelInfo]:
        """List available Perplexity models."""
        return [
            ModelInfo(
                id="sonar",
                name="Sonar",
                description="Balanced performance with web search",
                context_length=127072
            ),
            ModelInfo(
                id="sonar-pro",
                name="Sonar Pro",
                description="Advanced reasoning with web search",
                context_length=127072
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
        """Generate chat completion using Perplexity."""
        try:
            client = self._get_client(credentials)
            
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content or ""
            
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
            raise ProviderError(f"Perplexity chat failed: {str(e)}")


class GoogleProvider(BaseProvider):
    """Provider for Google Gemini models."""
    
    def __init__(self):
        super().__init__(
            id="google",
            label="Google",
            default_model="gemini-1.5-pro",
            supports_streaming=True,
            requires_api_key=True,
        )
    
    def _get_client(self, credentials: Dict[str, Any]):
        """Get Google Generative AI client."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ProviderError(
                "Google Generative AI package not installed. "
                "Install with: pip install google-generativeai"
            )
        
        api_key = credentials.get("api_key")
        if not api_key:
            raise ProviderAuthenticationError("Google API key is required")
        
        genai.configure(api_key=api_key)
        return genai
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Google API key."""
        try:
            genai = self._get_client(credentials)
            # List models as validation
            list(genai.list_models())
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg:
                raise ProviderAuthenticationError(f"Invalid Google API key: {str(e)}")
            raise ProviderError(f"Google validation failed: {str(e)}")
    
    def list_models(self, credentials: Dict[str, Any]) -> List[ModelInfo]:
        """List available Google models."""
        return [
            ModelInfo(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                description="Most capable model",
                context_length=2000000
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                description="Fast and efficient",
                context_length=1000000
            ),
            ModelInfo(
                id="gemini-2.0-flash-exp",
                name="Gemini 2.0 Flash (Experimental)",
                description="Latest experimental model",
                context_length=1000000
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
        """Generate chat completion using Google Gemini."""
        try:
            genai = self._get_client(credentials)
            
            # Create model instance
            model_instance = genai.GenerativeModel(model)
            
            # Convert messages to Gemini format (combines into single prompt)
            # Gemini uses a simpler format - we'll concatenate messages
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(f"Instructions: {msg.content}")
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"Assistant: {msg.content}")
            
            prompt = "\n\n".join(prompt_parts)
            
            # Generate content
            response = model_instance.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "top_p": kwargs.get("top_p", 0.95),
                }
            )
            
            content = response.text if hasattr(response, 'text') else ""
            
            # Google doesn't provide detailed usage in the same format
            usage = None
            if hasattr(response, 'usage_metadata'):
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            
            return ChatResponse(
                content=content,
                model=model,
                usage=usage,
                raw=None  # Can't easily serialize Gemini response
            )
        except Exception as e:
            raise ProviderError(f"Google Gemini chat failed: {str(e)}")


class GroqProvider(BaseProvider):
    """
    Provider for Groq (fast inference for open models).
    Uses OpenAI-compatible API.
    """
    
    def __init__(self):
        super().__init__(
            id="groq",
            label="Groq",
            default_model="llama-3.3-70b-versatile",
            supports_streaming=True,
            requires_api_key=True,
        )
    
    def _get_client(self, credentials: Dict[str, Any]):
        """Get OpenAI-compatible client for Groq."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ProviderError(
                "OpenAI package required for Groq. Install with: pip install openai"
            )
        
        api_key = credentials.get("api_key")
        if not api_key:
            raise ProviderAuthenticationError("Groq API key is required")
        
        return OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Groq API key."""
        try:
            client = self._get_client(credentials)
            client.models.list()
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                raise ProviderAuthenticationError(f"Invalid Groq API key: {str(e)}")
            raise ProviderError(f"Groq validation failed: {str(e)}")
    
    def list_models(self, credentials: Dict[str, Any]) -> List[ModelInfo]:
        """List available Groq models."""
        try:
            client = self._get_client(credentials)
            models_response = client.models.list()
            
            return [
                ModelInfo(
                    id=model.id,
                    name=model.id,
                    description=None,
                    context_length=None
                )
                for model in models_response.data
            ]
        except Exception:
            # Fallback to known models
            return [
                ModelInfo(
                    id="llama-3.3-70b-versatile",
                    name="Llama 3.3 70B",
                    description="Most capable Llama model",
                    context_length=32768
                ),
                ModelInfo(
                    id="llama-3.1-8b-instant",
                    name="Llama 3.1 8B",
                    description="Fast and efficient",
                    context_length=131072
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
        """Generate chat completion using Groq."""
        try:
            client = self._get_client(credentials)
            
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content or ""
            
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
            raise ProviderError(f"Groq chat failed: {str(e)}")


class OpenRouterProvider(BaseProvider):
    """
    Provider for OpenRouter (unified API for many models).
    Uses OpenAI-compatible API.
    """
    
    def __init__(self):
        super().__init__(
            id="openrouter",
            label="OpenRouter",
            default_model="anthropic/claude-3.5-sonnet",
            supports_streaming=True,
            requires_api_key=True,
        )
    
    def _get_client(self, credentials: Dict[str, Any]):
        """Get OpenAI-compatible client for OpenRouter."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ProviderError(
                "OpenAI package required for OpenRouter. Install with: pip install openai"
            )
        
        api_key = credentials.get("api_key")
        if not api_key:
            raise ProviderAuthenticationError("OpenRouter API key is required")
        
        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate OpenRouter API key."""
        try:
            client = self._get_client(credentials)
            client.models.list()
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg or "401" in error_msg:
                raise ProviderAuthenticationError(f"Invalid OpenRouter API key: {str(e)}")
            raise ProviderError(f"OpenRouter validation failed: {str(e)}")
    
    def list_models(self, credentials: Dict[str, Any]) -> List[ModelInfo]:
        """List available OpenRouter models."""
        try:
            client = self._get_client(credentials)
            models_response = client.models.list()
            
            # OpenRouter has many models, return popular ones
            return [
                ModelInfo(
                    id=model.id,
                    name=model.id,
                    description=None,
                    context_length=None
                )
                for model in models_response.data[:20]  # Limit to first 20
            ]
        except Exception:
            # Fallback to known popular models
            return [
                ModelInfo(
                    id="anthropic/claude-3.5-sonnet",
                    name="Claude 3.5 Sonnet",
                    description="Via OpenRouter",
                    context_length=200000
                ),
                ModelInfo(
                    id="openai/gpt-4-turbo",
                    name="GPT-4 Turbo",
                    description="Via OpenRouter",
                    context_length=128000
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
        """Generate chat completion using OpenRouter."""
        try:
            client = self._get_client(credentials)
            
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content or ""
            
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
            raise ProviderError(f"OpenRouter chat failed: {str(e)}")
