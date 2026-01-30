"""
Additional LLM providers: Perplexity, Google, Mistral, Groq, and OpenRouter.

These providers use OpenAI-compatible APIs or their own SDKs.
"""

from typing import Dict, Any, List
from .base import (
    BaseProvider, Message, ChatResponse, ModelInfo,
    ProviderError, ProviderAuthenticationError, ProviderConnectionError,
    ProviderRateLimitError, ProviderContextError,
    MessageAdapter, ParameterMapper
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
            ModelInfo(
                id="llama-3.1-sonar-small-128k-online",
                name="Llama 3.1 Sonar Small (Online)",
                description="Fast model with web search",
                context_length=127072
            ),
            ModelInfo(
                id="llama-3.1-sonar-large-128k-online",
                name="Llama 3.1 Sonar Large (Online)",
                description="Powerful model with web search",
                context_length=127072
            ),
            ModelInfo(
                id="llama-3.1-sonar-huge-128k-online",
                name="Llama 3.1 Sonar Huge (Online)",
                description="Most powerful model with web search",
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
            
            # Use MessageAdapter for OpenAI-compatible format
            openai_messages = MessageAdapter.to_openai(messages)
            
            # Map standard parameters to Perplexity equivalents
            mapped_params = ParameterMapper.map_params(kwargs, self.id)
            
            # 2025 best practices: top_p=0.9 for nucleus sampling, frequency_penalty for citation diversity
            # Perplexity-specific parameters must go in extra_body when using OpenAI client
            extra_body = {}
            
            # Disable search features to prevent returning web snippets instead of answers
            # These are Perplexity-specific params documented at:
            # https://docs.perplexity.ai/guides/chat-completions-guide
            if kwargs.get("disable_search", True):  # Default to disabling search for RAG use case
                extra_body["search_domain_filter"] = []  # Empty list disables domain filtering
                extra_body["return_images"] = False
                extra_body["return_related_questions"] = False
                # Note: search_recency_filter and return_citations are left unset
                # return_citations is NOT a documented parameter
            
            response = client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=mapped_params.get("top_p", 0.9),
                frequency_penalty=mapped_params.get("frequency_penalty", 0.3),
                extra_body=extra_body if extra_body else None,
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
            error_msg = str(e).lower()
            if "rate limit" in error_msg:
                raise ProviderRateLimitError(f"Perplexity rate limit exceeded: {str(e)}")
            elif "context" in error_msg or "maximum" in error_msg:
                raise ProviderContextError(f"Context too long for model {model}: {str(e)}")
            raise ProviderError(f"Perplexity chat failed: {str(e)}")


class GoogleProvider(BaseProvider):
    """Provider for Google Gemini models."""
    
    def __init__(self):
        super().__init__(
            id="google",
            label="Google",
            default_model="gemini-1.5-pro-latest",
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
        
        # Log SDK version for debugging
        print(f"[Google Provider] Using google-generativeai version: {genai.__version__ if hasattr(genai, '__version__') else 'unknown'}")
        print(f"[Google Provider] API key present: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
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
        # Note: Model names like 'gemini-1.5-pro-latest' are valid
        # The SDK automatically adds 'models/' prefix internally
        return [
            ModelInfo(
                id="gemini-1.5-pro-latest",
                name="Gemini 1.5 Pro (Latest)",
                description="Most capable model, auto-updated",
                context_length=2000000
            ),
            ModelInfo(
                id="gemini-1.5-flash-latest",
                name="Gemini 1.5 Flash (Latest)",
                description="Fast and efficient, auto-updated",
                context_length=1000000
            ),
            ModelInfo(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro (Stable)",
                description="Stable version, not auto-updated",
                context_length=2000000
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash (Stable)",
                description="Fast stable version",
                context_length=1000000
            ),
            ModelInfo(
                id="gemini-2.0-flash-exp",
                name="Gemini 2.0 Flash (Experimental)",
                description="Latest experimental model",
                context_length=1000000
            ),
            ModelInfo(
                id="gemini-pro",
                name="Gemini Pro (Legacy)",
                description="Earlier Gemini model",
                context_length=32000
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
            
            # Use MessageAdapter for Gemini-specific format
            system_instruction, gemini_history = MessageAdapter.to_gemini(messages)
            
            # Map standard parameters to Google equivalents
            mapped_params = ParameterMapper.map_params(kwargs, self.id)
            
            # Configure safety settings to prevent over-blocking
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            # Create model instance with system instruction
            print(f"[Google Provider] Creating GenerativeModel with model='{model}'")
            print(f"[Google Provider] System instruction length: {len(system_instruction) if system_instruction else 0}")
            
            try:
                model_instance = genai.GenerativeModel(
                    model,
                    system_instruction=system_instruction,
                    safety_settings=safety_settings
                )
                print(f"[Google Provider] Model instance created successfully")
            except Exception as model_error:
                print(f"[Google Provider] ERROR creating model: {type(model_error).__name__}: {model_error}")
                raise
            
            # Use adapted Gemini message format
            # Gemini expects alternating user/model turns in chat history
            if len(gemini_history) == 1 and gemini_history[0]["role"] == "user":
                # Single turn - use generate_content
                response = model_instance.generate_content(
                    gemini_history[0]["parts"][0],
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                        "top_p": mapped_params.get("top_p", 0.95),
                        "top_k": mapped_params.get("top_k", 40),
                    }
                )
            else:
                # Multi-turn - use chat with history
                chat = model_instance.start_chat(history=gemini_history[:-1])
                response = chat.send_message(
                    gemini_history[-1]["parts"][0],
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                        "top_p": mapped_params.get("top_p", 0.95),
                        "top_k": mapped_params.get("top_k", 40),
                    }
                )
            
            # Extract text from response
            content = ""
            if hasattr(response, 'text'):
                content = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Extract from candidates if text attribute not available
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    content = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
            
            if not content:
                raise ProviderError("No content in Google Gemini response")
            
            # Google usage metadata
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
            # Provide more detailed error information
            error_msg = str(e)
            if hasattr(e, 'message'):
                error_msg = e.message
            error_msg_lower = error_msg.lower()
            if "rate limit" in error_msg_lower or "quota" in error_msg_lower:
                raise ProviderRateLimitError(f"Google Gemini rate limit exceeded: {error_msg}")
            elif "context" in error_msg_lower or "token" in error_msg_lower:
                raise ProviderContextError(f"Context too long for model {model}: {error_msg}")
            raise ProviderError(f"Google Gemini chat failed: {error_msg}")


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
            
            # Use MessageAdapter for OpenAI-compatible format
            openai_messages = MessageAdapter.to_openai(messages)
            
            # Map standard parameters to Groq equivalents
            mapped_params = ParameterMapper.map_params(kwargs, self.id)
            
            # 2025 best practices: top_p=0.9 for nucleus sampling, frequency_penalty for citation diversity
            response = client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=mapped_params.get("top_p", 0.9),
                frequency_penalty=mapped_params.get("frequency_penalty", 0.3),
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
            error_msg = str(e).lower()
            if "rate limit" in error_msg:
                raise ProviderRateLimitError(f"Groq rate limit exceeded: {str(e)}")
            elif "context" in error_msg or "maximum" in error_msg:
                raise ProviderContextError(f"Context too long for model {model}: {str(e)}")
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
            
            # Use MessageAdapter for OpenAI-compatible format
            openai_messages = MessageAdapter.to_openai(messages)
            
            # Map standard parameters to OpenRouter equivalents
            mapped_params = ParameterMapper.map_params(kwargs, self.id)
            
            # 2025 best practices: top_p=0.9 for nucleus sampling, frequency_penalty for citation diversity
            response = client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=mapped_params.get("top_p", 0.9),
                frequency_penalty=mapped_params.get("frequency_penalty", 0.3),
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
            error_msg = str(e).lower()
            if "rate limit" in error_msg:
                raise ProviderRateLimitError(f"OpenRouter rate limit exceeded: {str(e)}")
            elif "context" in error_msg or "maximum" in error_msg:
                raise ProviderContextError(f"Context too long for model {model}: {str(e)}")
            raise ProviderError(f"OpenRouter chat failed: {str(e)}")
