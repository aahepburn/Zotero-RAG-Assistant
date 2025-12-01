"""
Conversation Store for managing stateful chat sessions.

Provides in-memory storage of conversation histories with support for:
- Multi-turn conversation tracking
- Context window management (truncation)
- Session lifecycle management
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from backend.model_providers import Message


@dataclass
class ConversationHistory:
    """Represents a chat session's conversation history."""
    session_id: str
    messages: List[Message]
    system_prompt: Optional[str] = None
    

class ConversationStore:
    """
    In-memory storage for conversation histories across chat sessions.
    
    Each session maintains its own message list with roles: system, user, assistant.
    Designed for easy migration to persistent storage (database/files) later.
    """
    
    def __init__(self):
        # Maps session_id -> ConversationHistory
        self._sessions: Dict[str, ConversationHistory] = {}
        
        # Default system prompt for new sessions
        self.default_system_prompt = (
            "You are an expert research assistant helping an academic researcher "
            "understand their Zotero library. You have access to their academic papers "
            "and can answer questions about their research. Always cite sources using "
            "the provided citation numbers [1], [2], etc. Be precise and scholarly in "
            "your responses."
        )
    
    def get_messages(self, session_id: str) -> List[Message]:
        """
        Retrieve the message history for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of messages in chronological order, including system prompt
        """
        if session_id not in self._sessions:
            # Initialize new session with system prompt
            self._sessions[session_id] = ConversationHistory(
                session_id=session_id,
                messages=[Message(role="system", content=self.default_system_prompt)],
                system_prompt=self.default_system_prompt
            )
        
        return self._sessions[session_id].messages.copy()
    
    def append_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a new message to the session history.
        
        Args:
            session_id: Unique session identifier
            role: Message role ("user" or "assistant")
            content: Message content
        """
        # Ensure session exists
        if session_id not in self._sessions:
            self.get_messages(session_id)  # Initialize with system prompt
        
        message = Message(role=role, content=content)
        self._sessions[session_id].messages.append(message)
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all messages from a session.
        
        Args:
            session_id: Unique session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists and has messages."""
        return session_id in self._sessions and len(self._sessions[session_id].messages) > 0
    
    def get_session_count(self) -> int:
        """Get the total number of active sessions."""
        return len(self._sessions)
    
    def trim_messages_for_context(
        self, 
        messages: List[Message], 
        max_messages: int = 20,
        max_chars: int = 8000
    ) -> List[Message]:
        """
        Trim conversation history to fit within context window constraints.
        
        Strategy:
        1. Always keep the system message (first message)
        2. Keep the most recent N messages within character limit
        3. Prefer keeping complete user-assistant pairs
        
        Args:
            messages: Full message history
            max_messages: Maximum number of messages to keep (excluding system)
            max_chars: Maximum total characters (approximate token limit)
            
        Returns:
            Trimmed message list that fits constraints
        """
        if not messages:
            return []
        
        # Separate system message from conversation
        system_message = None
        conversation_messages = messages
        
        if messages[0].role == "system":
            system_message = messages[0]
            conversation_messages = messages[1:]
        
        # If already within limits, return as-is
        total_chars = sum(len(m.content) for m in messages)
        if len(conversation_messages) <= max_messages and total_chars <= max_chars:
            return messages
        
        # Keep most recent messages within limits
        kept_messages = []
        char_count = len(system_message.content) if system_message else 0
        
        # Work backwards from most recent
        for msg in reversed(conversation_messages):
            msg_chars = len(msg.content)
            if (len(kept_messages) < max_messages and 
                char_count + msg_chars <= max_chars):
                kept_messages.insert(0, msg)
                char_count += msg_chars
            else:
                break
        
        # Reconstruct with system message first
        result = []
        if system_message:
            result.append(system_message)
        result.extend(kept_messages)
        
        return result
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get metadata about a session.
        
        Returns:
            Dictionary with session stats or None if session doesn't exist
        """
        if session_id not in self._sessions:
            return None
        
        history = self._sessions[session_id]
        messages = history.messages
        
        user_msgs = [m for m in messages if m.role == "user"]
        assistant_msgs = [m for m in messages if m.role == "assistant"]
        total_chars = sum(len(m.content) for m in messages)
        
        return {
            "session_id": session_id,
            "total_messages": len(messages),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "total_characters": total_chars,
            "has_system_prompt": any(m.role == "system" for m in messages)
        }
