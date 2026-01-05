# Perplexity-Style Multi-Turn Conversational RAG

## Overview

This document explains the implementation of Perplexity-style conversational RAG for the Zotero-RAG-Assistant, fixing the "I'm ready to begin" issue and enabling proper follow-up question handling.

## The Problem: "I'm Ready to Begin" Responses

### Root Cause Analysis

Your chatbot was responding with meta-cognitive acknowledgments ("Okay, I understand. I'm ready to begin") instead of answering follow-up questions. This happened because:

1. **System instructions were being embedded in user messages** - Each turn included RAG context with academic instructions, which the LLM interpreted as new directives requiring acknowledgment

2. **Missing query condensation step** - Follow-up questions like "Is there an overlap?" weren't being converted to standalone queries before retrieval, causing:
   - Retrieval of wrong documents (searching for "is there overlap" instead of "overlap between multi-task learning and causal approaches")
   - Loss of anaphoric reference resolution (pronouns like "it", "that approach" lost their meaning)
   - Failed comparative questions (missing one or both comparison targets)

3. **Incorrect message construction** - For follow-ups, the system was re-injecting instructions instead of simply appending the user's question to the existing conversation

## The Solution: Three-Step RAG Pipeline

### Architecture

```

  STEP 1: CONDENSE (Query Rewriting)                             

  Input:   "Is there an overlap?"                                
  History: [previous discussion about MTL and causal inference]  
  Output:  "Is there an overlap between multi-task learning      
            in NLP and causal inference approaches?"             
                                                                  
  Purpose: Convert context-dependent follow-ups into standalone  
           queries suitable for semantic search                  



  STEP 2: RETRIEVE (Vector Search)                               

  Input:   Standalone query from Step 1                          
  Process: 1. Hybrid search (dense embeddings + BM25)            
           2. Retrieve top 15 candidates                          
           3. Re-rank with cross-encoder → top 6-8               
  Output:  Relevant paper snippets with citations                
                                                                  
  Purpose: Find evidence using semantically complete query       



  STEP 3: GENERATE (Answer Synthesis)                            

  Messages:                                                       
    [0] system:    "You are an academic research assistant..."   
    [1] user:      "What is MTL?" + [evidence snippets]          
    [2] assistant: "Multi-task learning (MTL) is..."             
    [3] user:      "Is there an overlap?"  ← PLAIN QUESTION ONLY 
                                                                  
  Purpose: Continue conversation naturally using history         
           WITHOUT re-injecting instructions                     

```

## Implementation Details

### 1. Query Condensation (`backend/query_condenser.py`)

**Purpose**: Converts follow-up questions into standalone queries

**Key Components**:

```python
class QueryCondenser:
    def condense_query(self, query: str, conversation_history: List[Message]) -> str:
        """
        Condense a follow-up query using conversation history.
        
        Example:
            History: "What is multi-task learning?"
            Query: "Is there overlap with causal approaches?"
            Output: "Is there overlap between multi-task learning and causal approaches?"
        """
```

**When to condense** (heuristics implemented in `should_condense`):
- Query contains pronouns: "it", "they", "that", "these"
- Query contains elliptical constructions: "what about", "how about", "also"
- Query contains comparative language: "overlap", "relationship", "compare"
- Short queries (<8 words) after turn 1

**Prompt Strategy**:
- **Task**: Extraction/rewriting (NOT instruction-following)
- **Temperature**: 0.2 (low for precision)
- **Max tokens**: 150 (standalone queries should be concise)
- **Output constraint**: "Output ONLY the standalone question" (prevents meta-responses)

### 2. Message Construction (`backend/interface.py`)

**Critical Fix**: Different message structures for first turn vs. follow-ups

#### First Turn (Turn 1)
```python
user_message = f"""{question}

---
**Evidence from library:**

[1] Paper Title (2024)
Authors
Relevant passage...

[2] Another Paper (2023)
...
"""
```

#### Follow-Up Turns (Turn 2+)
```python
# WRONG - Causes "I'm ready to begin" responses:
user_message = f"""{question}

---
**Instructions:**
Answer using the evidence above...  ← LLM reads this as NEW directive!
"""

# CORRECT - Natural conversation continuation:
user_message = query  # Just the plain question!
```

**Why this works**:
- System prompt is sent ONCE at session start (in conversation history)
- Follow-ups simply append user question → model continues conversation naturally
- New evidence (if retrieved) added as a separate note AFTER user question

### 3. Conversation History Management

**System Prompt** (`backend/conversation_store.py`):
- Injected ONCE when session is created
- Contains comprehensive instructions (academic writing, citation rules, conversation handling)
- Never repeated in subsequent turns

**Context Window Trimming**:
```python
def trim_messages_for_context(messages, max_messages=20, max_chars=8000):
    """
    Keep:
    - System message (always first)
    - Most recent N user/assistant pairs
    - Within ~2000 token limit
    """
```

## Usage Examples

### Example 1: Comparative Follow-Up

**Turn 1**:
```
User: "What is multi-task learning in NLP?"
→ Retrieval: "multi-task learning in NLP"
→ Response: [explanation with citations]
```

**Turn 2**:
```
User: "Is there an overlap with causal approaches?"
→ Condensation: "Is there overlap between multi-task learning in NLP and causal inference approaches?"
→ Retrieval: Uses condensed query
→ Message: Plain question appended to history
→ Response: "Yes, there is significant overlap [1][2]..."
```

### Example 2: Pronoun Resolution

**Turn 1**:
```
User: "How does BERT handle contextualized embeddings?"
→ Response: [explanation]
```

**Turn 2**:
```
User: "How does it compare to GPT?"
→ Condensation: "How does BERT's handling of contextualized embeddings compare to GPT?"
→ Retrieval: Finds relevant passages about both models
→ Response: "BERT and GPT differ in several ways [1][3]..."
```

### Example 3: Clarification Request

**Turn 1**:
```
User: "What are the main challenges in few-shot learning?"
→ Response: [lists challenges including data efficiency]
```

**Turn 2**:
```
User: "Can you elaborate on the data efficiency issue?"
→ Condensation: "Can you elaborate on the data efficiency challenges in few-shot learning?"
→ Retrieval: Retrieves focused passages on data efficiency
→ Response: "The data efficiency challenge in few-shot learning refers to..."
```

## Key Differences from Your Original Implementation

| Aspect | Original (Broken) | Fixed (Perplexity-style) |
|--------|------------------|--------------------------|
| **Query for Retrieval** | User's raw question | Condensed standalone query |
| **Follow-up Messages** | Question + embedded instructions | Plain question only |
| **System Prompt** | Potentially re-injected | Sent once at session start |
| **Pronoun Resolution** | Lost ("it" → searches for "it") | Resolved via condensation |
| **Message Structure** | All turns identical | First turn ≠ follow-up turns |

## Prompt Engineering Details

### Condensation Prompt (Critical Section)

```python
CONDENSE_PROMPT = """You are converting a follow-up question into a standalone question.

## Task
Rephrase the follow-up by:
1. **Replacing pronouns** with specific nouns
2. **Including implicit context** from history
3. **Maintaining original intent** exactly
4. **Making it suitable for semantic search**

## Rules
- **Output ONLY the standalone question** - no explanations
- Keep question format
- Preserve key terms exactly
- Don't add information not implied by history
- Be concise

[Examples provided showing transformations]
"""
```

**Why this works**:
- Task framing: "converting" (extraction) not "answering" (generation)
- Output constraint: "ONLY the standalone question" prevents preambles
- Examples demonstrate the exact transformation pattern
- No invitation for meta-cognitive responses

### System Prompt (Academic Instructions)

Located in `backend/academic_prompts.py`:

```python
SYSTEM_PROMPT = """You are an expert academic research assistant...

## Conversation Handling
This is a **multi-turn conversation**. You should:
- **Remember context**: Reference earlier discussion
- **Answer naturally**: Respond directly to follow-ups
- **Don't reset**: Never say "I'm ready to begin"
- **Synthesize**: Connect follow-ups to earlier topics

## Citation Requirements
[Detailed citation rules...]

## Response Structure
[Format guidelines...]
"""
```

## Configuration Parameters

### Query Condensation
```python
temperature=0.2      # Low for precise extraction
max_tokens=150       # Standalone queries should be brief
top_p=0.9           # Standard nucleus sampling
```

### Answer Generation
```python
temperature=0.35     # Balance factuality with synthesis
max_tokens=2000      # Allow detailed academic responses
top_p=0.9           # Nucleus sampling
top_k=50            # Moderate vocabulary diversity
repeat_penalty=1.15  # Prevent repetition
```

## Testing the Implementation

### Manual Test Cases

1. **First Turn** (baseline):
   ```
   Query: "What is few-shot learning?"
   Expected: Normal academic answer with citations
   ```

2. **Pronoun Follow-up**:
   ```
   Turn 1: "What is BERT?"
   Turn 2: "How does it work?"
   Expected: Answers about BERT, NOT meta-response
   ```

3. **Comparative Follow-up**:
   ```
   Turn 1: "What is multi-task learning?"
   Turn 2: "Is there overlap with transfer learning?"
   Expected: Comparison answer, NOT "I'm ready to begin"
   ```

4. **Elliptical Follow-up**:
   ```
   Turn 1: "What are attention mechanisms?"
   Turn 2: "What about self-attention?"
   Expected: Explanation of self-attention
   ```

### Debugging Tips

Check terminal output for diagnostic messages:
```
 Detected follow-up question, condensing...
 Query condensation:
   Original: Is there an overlap?
   Standalone: Is there an overlap between multi-task learning and causal inference?
 Follow-up turn (#2): plain question only
 Added 6 new snippets as evidence note
```

## Performance Considerations

### Context Window Management
- **System prompt**: ~800 tokens (sent once)
- **Evidence per turn**: ~1200 tokens (6 snippets × 200 tokens)
- **History**: Up to 20 messages (~4000 tokens)
- **Total**: ~6000 tokens (safe for 8K context models)

### Latency Breakdown
1. Query condensation: ~1-2s (single LLM call)
2. Vector retrieval: ~0.5s (hybrid search)
3. Re-ranking: ~0.3s (cross-encoder)
4. Answer generation: ~3-5s (LLM call)
**Total**: ~5-8s per turn

### Optimization Opportunities
- Cache condensed queries (avoid re-condensing similar follow-ups)
- Parallel retrieval + condensation (if query is obviously new)
- Streaming responses (show answer as it generates)

## Common Pitfalls to Avoid

 **Don't**: Embed instructions in follow-up user messages
 **Do**: Keep follow-ups as plain questions

 **Don't**: Use raw follow-up questions for retrieval
 **Do**: Condense them first using conversation history

 **Don't**: Re-inject the system prompt each turn
 **Do**: Send it once and maintain conversation history

 **Don't**: Truncate context too aggressively
 **Do**: Keep enough history for coherent conversation

 **Don't**: Use high temperature for condensation
 **Do**: Use low temperature (0.2) for accurate extraction

## References

- **Perplexity Architecture**: Multi-step RAG with query rewriting
- **LangChain ConversationalRetrievalChain**: Query condensation pattern
- **Academic RAG Best Practices**: Citation-aware prompting, grounding requirements
- **Industry Patterns**: Anthropic Claude chat, OpenAI GPT assistants

## Future Enhancements

1. **Conversation Memory Management**:
   - Persist conversations to database
   - Semantic compression of long histories
   - Smart forgetting of irrelevant context

2. **Advanced Query Condensation**:
   - Multi-query generation for ambiguous follow-ups
   - Entity extraction and linking
   - Temporal reasoning ("earlier you mentioned X")

3. **Retrieval Improvements**:
   - Query expansion using conversation themes
   - Dynamic k-selection based on query complexity
   - Diversity-aware re-ranking

4. **User Experience**:
   - Show condensed query to user (transparency)
   - Allow manual override of condensation
   - Suggested follow-up questions

---

**Implementation Status**:  Complete and tested

**Files Modified**:
- `backend/query_condenser.py` (new)
- `backend/interface.py` (updated chat method)
- `backend/conversation_store.py` (already correct)
- `backend/academic_prompts.py` (already correct)
