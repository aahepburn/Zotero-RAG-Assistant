"""
Base interface for LLM providers.

Defines the ModelProvider protocol that all concrete providers must implement.
This ensures a consistent interface regardless of whether using local models (Ollama)
or cloud APIs (OpenAI, Anthropic, etc.).
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Standard message format for chat interactions."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatResponse:
    """Normalized response from any LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None  # {"prompt_tokens": X, "completion_tokens": Y}
    raw: Optional[Dict[str, Any]] = None  # Raw response for debugging


@dataclass
class ModelInfo:
    """Information about an available model."""
    id: str
    name: str
    description: Optional[str] = None
    context_length: Optional[int] = None


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass


class ProviderConnectionError(ProviderError):
    """Raised when unable to connect to provider."""
    pass


class ProviderAuthenticationError(ProviderError):
    """Raised when authentication fails."""
    pass


class ModelProvider(Protocol):
    """
    Protocol defining the interface all LLM providers must implement.
    
    Providers should implement this interface to work with the chatbot system.
    Each provider handles its own API authentication, request formatting,
    and response normalization.
    """
    
    @property
    def id(self) -> str:
        """Unique identifier for this provider (e.g., 'ollama', 'openai')."""
        ...
    
    @property
    def label(self) -> str:
        """Human-readable label for UI display (e.g., 'Ollama (Local)', 'OpenAI')."""
        ...
    
    @property
    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming responses."""
        ...
    
    @property
    def default_model(self) -> str:
        """Default model ID for this provider."""
        ...
    
    @property
    def requires_api_key(self) -> bool:
        """Whether this provider requires an API key."""
        ...
    
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        Validate that the provided credentials are valid.
        
        Args:
            credentials: Dictionary containing provider-specific credentials
                        (e.g., {"api_key": "sk-..."})
        
        Returns:
            True if credentials are valid, False otherwise
            
        Raises:
            ProviderConnectionError: If unable to reach provider
            ProviderAuthenticationError: If credentials are invalid
        """
        ...
    
    def list_models(self, credentials: Dict[str, Any]) -> List[ModelInfo]:
        """
        Get list of available models from this provider.
        
        Args:
            credentials: Provider-specific credentials
            
        Returns:
            List of available models with metadata
            
        Raises:
            ProviderError: If unable to retrieve models
        """
        ...
    
    def chat(
        self,
        credentials: Dict[str, Any],
        model: str,
        messages: List[Message],
        temperature: float = 0.3,
        max_tokens: int = 512,
        **kwargs
    ) -> ChatResponse:
        """
        Generate a chat completion using this provider.
        
        Args:
            credentials: Provider-specific credentials
            model: Model ID to use for generation
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Normalized ChatResponse object
            
        Raises:
            ProviderError: If generation fails
        """
        ...


class BaseProvider:
    """
    Base class with common functionality for providers.
    
    Concrete providers can inherit from this to get standard implementations
    of common methods and utilities.
    """
    
    def __init__(
        self,
        id: str,
        label: str,
        default_model: str,
        supports_streaming: bool = False,
        requires_api_key: bool = True,
    ):
        self._id = id
        self._label = label
        self._default_model = default_model
        self._supports_streaming = supports_streaming
        self._requires_api_key = requires_api_key
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def label(self) -> str:
        return self._label
    
    @property
    def supports_streaming(self) -> bool:
        return self._supports_streaming
    
    @property
    def default_model(self) -> str:
        return self._default_model
    
    @property
    def requires_api_key(self) -> bool:
        return self._requires_api_key
    
    def _check_credentials(self, credentials: Dict[str, Any], required_keys: List[str]):
        """Helper to validate required credential keys are present."""
        missing = [key for key in required_keys if not credentials.get(key)]
        if missing:
            raise ProviderAuthenticationError(
                f"Missing required credentials for {self.id}: {', '.join(missing)}"
            )
