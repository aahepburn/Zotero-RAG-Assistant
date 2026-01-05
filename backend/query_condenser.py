"""
Query Condensation for Multi-Turn Conversational RAG.

Converts context-dependent follow-up questions into standalone queries
suitable for vector database retrieval.

Based on Perplexity-style conversational RAG architecture:
- Isolates retrieval logic from conversation logic
- Maintains semantic fidelity to original intent
- Prevents retrieval of irrelevant context
"""

from typing import List
from backend.model_providers import Message, ProviderManager


class QueryCondenser:
    """
    Condenses follow-up questions into standalone queries using conversation history.
    
    This is the critical component for multi-turn RAG systems. Without it:
    - Follow-ups like "Is there overlap?" retrieve wrong documents
    - Anaphoric references ("it", "that approach") lose context
    - Comparative questions fail to identify all comparison targets
    
    With condensation:
    - "Is there overlap?" → "Is there overlap between multi-task learning and causal approaches?"
    - "How does it work?" → "How does multi-task learning in NLP work?"
    - "What about X?" → "What about X in relation to [previous topic]?"
    """
    
    # Prompt for query condensation
    # Critical: This must NOT trigger "I'm ready" responses
    # It asks for EXTRACTION, not new instructions
    CONDENSE_PROMPT = """You are converting a follow-up question into a standalone question by incorporating relevant context from the conversation history.

## Task

Given a conversation history and a follow-up question, rephrase the follow-up into a standalone question that:
1. **Replaces pronouns** (it, they, that, these) with specific nouns
2. **Includes implicit context** needed to understand the question
3. **Maintains the original intent** exactly
4. **Is suitable for semantic search** (clear, self-contained)

## Rules

- **Output ONLY the standalone question** - no explanations, no preamble
- **Keep the question format** - if input is a question, output is a question
- **Preserve key terms** from the follow-up exactly
- **Don't add information** not implied by the history
- **Be concise** - only add necessary context

## Examples

**Conversation:**
User: What is multi-task learning in NLP?
Assistant: Multi-task learning (MTL) in NLP is a training paradigm where...

**Follow-up:** Is there an overlap with causal approaches?
**Standalone:** Is there an overlap between multi-task learning in NLP and causal inference approaches?

---

**Conversation:**
User: How does BERT handle contextualized embeddings?
Assistant: BERT generates contextualized embeddings through...

**Follow-up:** What about GPT?
**Standalone:** How does GPT handle contextualized embeddings?

---

**Conversation:**
User: What are the main challenges in few-shot learning?
Assistant: The main challenges include limited training data...

**Follow-up:** Can you elaborate on the data efficiency issue?
**Standalone:** Can you elaborate on the data efficiency challenges in few-shot learning?

---

Now do the same for the conversation below."""

    def __init__(self, provider_manager: ProviderManager):
        """
        Initialize query condenser with LLM provider.
        
        Args:
            provider_manager: Configured LLM provider for condensation
        """
        self.provider_manager = provider_manager
    
    def condense_query(
        self, 
        query: str, 
        conversation_history: List[Message],
        max_history_chars: int = 1500
    ) -> str:
        """
        Condense a follow-up query into a standalone query using conversation history.
        
        Args:
            query: User's follow-up question (may contain pronouns, implicit references)
            conversation_history: Recent conversation messages (system, user, assistant)
            max_history_chars: Maximum characters of history to include (default 1500)
            
        Returns:
            Standalone query suitable for retrieval, or original query if condensation fails
        """
        # Filter out system messages and take only recent history
        relevant_history = [
            m for m in conversation_history 
            if m.role in ["user", "assistant"]
        ][-6:]  # Last 3 turns (6 messages)
        
        # Build compact history representation
        history_lines = []
        total_chars = 0
        for msg in relevant_history:
            prefix = "User:" if msg.role == "user" else "Assistant:"
            # Truncate long messages to avoid context overflow
            content = msg.content[:500] if len(msg.content) > 500 else msg.content
            line = f"{prefix} {content}"
            
            if total_chars + len(line) > max_history_chars:
                break
            history_lines.append(line)
            total_chars += len(line)
        
        if not history_lines:
            # No history - return query as-is
            return query
        
        history_str = "\n".join(history_lines)
        
        # Build condensation prompt
        full_prompt = f"""{self.CONDENSE_PROMPT}

## Conversation History

{history_str}

## Follow-up Question

{query}

## Standalone Question"""
        
        # Call LLM with focused parameters (low temperature for accuracy)
        try:
            messages = [Message(role="user", content=full_prompt)]
            response = self.provider_manager.chat(
                messages=messages,
                temperature=0.2,  # Low temperature for precise extraction
                max_tokens=150,   # Standalone query should be concise
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1
            )
            
            standalone_query = response.content.strip()
            
            # Validation: ensure we got a reasonable query back
            if len(standalone_query) < 5 or len(standalone_query) > 300:
                print(f"Warning: Condensed query seems malformed ({len(standalone_query)} chars), using original")
                return query
            
            # Remove common artifacts from LLM responses
            standalone_query = standalone_query.strip('"').strip("'")
            if standalone_query.lower().startswith("standalone question:"):
                standalone_query = standalone_query[20:].strip()
            
            print(f" Query condensation:")
            print(f"   Original: {query}")
            print(f"   Standalone: {standalone_query}")
            
            return standalone_query
            
        except Exception as e:
            print(f"Query condensation failed: {e}")
            # Fallback to original query
            return query
    
    def should_condense(
        self, 
        query: str, 
        conversation_history: List[Message]
    ) -> bool:
        """
        Determine if a query needs condensation based on heuristics.
        
        Args:
            query: User's question
            conversation_history: Recent messages
            
        Returns:
            True if query appears to be a follow-up requiring condensation
        """
        # If no history (first turn), no condensation needed
        user_messages = [m for m in conversation_history if m.role == "user"]
        if len(user_messages) == 0:
            return False
        
        q = query.lower().strip()
        
        # Check for anaphoric references (pronouns that need resolution)
        has_anaphora = any(
            # Pronouns and determiners
            (q.startswith(word + " ") or f" {word} " in q or q.endswith(" " + word))
            for word in ["it", "they", "them", "that", "this", "these", "those", "its", "their"]
        )
        
        # Check for formal anaphoric expressions
        has_formal_anaphora = any(phrase in q for phrase in [
            "said", "such", "aforementioned", "the former", "the latter"
        ])
        
        # Check for elliptical constructions (incomplete sentences)
        has_ellipsis = any(phrase in q for phrase in [
            "what about", "how about", "and", "also", "additionally",
            "the above", "the previous", "earlier", "you mentioned",
            "as mentioned", "like you said"
        ])
        
        # Check for comparative language (likely needs both topics)
        has_comparison = any(phrase in q for phrase in [
            "overlap", "relationship", "compare", "contrast", "versus", "vs",
            "difference", "similar", "relate", "connection", "between"
        ])
        
        # Short queries (<8 words) after turn 1 are likely follow-ups
        is_short = len(q.split()) < 8
        
        # Condense if any strong signal is present
        should_cond = has_anaphora or has_formal_anaphora or has_ellipsis or (has_comparison and is_short)
        
        if should_cond:
            print(f"[QueryCondenser] should_condense=True: anaphora={has_anaphora}, formal_anaphora={has_formal_anaphora}, ellipsis={has_ellipsis}, comparison={has_comparison}, short={is_short}")
        
        return should_cond


# Export
__all__ = ["QueryCondenser"]
