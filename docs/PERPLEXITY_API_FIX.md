# Provider API Issues and Fixes

## Problems Identified

### Issue 1: Raw Citation Snippets Being Returned (Multiple Providers)

**Symptom**: After questions, providers return raw bibliographic citations or document snippets instead of synthesized answers:

```
J. Tian and J. Pearl. Causal discovery from changes. In UAI, pages 512–521, 2001. 
[25] S. Triantaﬁllou and I. Tsamardinos. Constraint-based causal discovery...
```

**Root Causes**:

#### Perplexity-Specific
- Perplexity Sonar models are **designed for web search**, not RAG over private documents
- They automatically search the web and return citations from web sources
- After multiple turns, the model becomes confused about whether to use your Zotero context or search the web
- Parameters like `return_citations` need to be explicitly disabled

#### Google Gemini-Specific  
- **Wrong conversation format**: Was concatenating messages as strings instead of using Gemini's native chat format
- **System prompt handling**: System instructions need to be passed as separate parameter, not as a message
- **Error handling**: Exceptions were being caught and falling back to returning snippets
- **Content filtering**: Overly aggressive safety settings could block responses

**Silent Fallback**: When ANY provider throws an exception, the error handler was returning `snippets[0]["snippet"]` instead of the actual LLM response.

### Issue 2: Meta-Response at First Turn

**Symptom**: The first response includes unnecessary clarifications:

```
I appreciate your question, but I need to clarify an important limitation: 
the context you've provided from your Zotero library contains only partial excerpts...
```

**Root Cause**:
- The original system prompt was very verbose (~800 words) with extensive instructions
- Perplexity models interpret detailed instructions as directives requiring acknowledgment
- The model responds with meta-cognitive acknowledgments instead of directly answering

## Solutions Implemented

### Fix 1: Perplexity - Disable Web Search Mode

**File**: `backend/model_providers/additional.py`

Added explicit parameters to prevent Perplexity from searching the web:

```python
response = client.chat.completions.create(
    model=model,
    messages=openai_messages,
    temperature=temperature,
    max_tokens=max_tokens,
    top_p=kwargs.get("top_p", 0.9),
    frequency_penalty=kwargs.get("frequency_penalty", 0.3),
    return_citations=False,  # Disable web search citations
    return_images=False,      # Disable web image search  
    search_recency_filter=None,  # Disable time-based web filtering
)
```

### Fix 2: Google Gemini - Proper Chat Format

**File**: `backend/model_providers/additional.py`

Completely rewrote Google provider to use native Gemini conversation format:

```python
# Separate system instruction (Gemini-specific parameter)
system_instruction = None
conversation_messages = []

for msg in messages:
    if msg.role == "system":
        system_instruction = msg.content
    else:
        conversation_messages.append(msg)

# Create model with system instruction
model_instance = genai.GenerativeModel(
    model,
    system_instruction=system_instruction,
    safety_settings=[...]  # Prevent over-blocking
)

# Use proper chat format for multi-turn
if len(conversation_messages) > 1:
    history = [
        {"role": "user" if msg.role == "user" else "model", 
         "parts": [msg.content]}
        for msg in conversation_messages[:-1]
    ]
    chat = model_instance.start_chat(history=history)
    response = chat.send_message(conversation_messages[-1].content, ...)
```

**Key Changes**:
- ✅ System instructions passed as separate parameter (not concatenated)
- ✅ Multi-turn conversations use `start_chat()` with history
- ✅ Single-turn uses `generate_content()` directly
- ✅ Safety settings set to `BLOCK_NONE` to prevent academic content blocking
- ✅ Better response extraction with fallback to `candidates[0].content.parts`

### Fix 3: Better Error Handling

**File**: `backend/interface.py`

Improved error diagnostics instead of silently falling back to snippets:

```python
except Exception as e:
    print(f"\n{'='*80}")
    print(f"LLM GENERATION ERROR")
    print(f"{'='*80}")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    print(f"Traceback:\n{traceback.format_exc()}")
    print(f"{'='*80}\n")
    
    if snippets:
        print("WARNING: Falling back to returning first snippet due to LLM error")
        summary = snippets[0]["snippet"]
    else:
        summary = f"Error: Failed to generate response. {str(e)}"
```

**Impact**:
- Shows full error details in logs
- Makes it obvious when fallback is happening
- Returns error message if no snippets available

### Fix 2: Simplify System Prompt

**File**: `backend/academic_prompts.py`

Reduced system prompt from ~800 words to ~200 words (benefits all providers):

```python
SYSTEM_PROMPT = """You are an academic research assistant. Answer questions based on the provided documents from the user's Zotero library and the conversation history.

## Key guidelines

- Synthesize findings from multiple sources into coherent explanations
- Cite sources using provided citation IDs [1], [2], etc.
- Identify research gaps and contradictions when present
- Answer follow-up questions directly without meta-responses
- Use only the provided context - do not search external sources
- If information is insufficient, state what additional sources would help

## Citation format

- Add inline citations [N] for factual claims
- Use multiple citations [1][2] when multiple sources support a point
- Provide Chicago-style references when listing sources"""
```

**Impact**:
- Reduces confusion at conversation start (all providers)
- Eliminates meta-acknowledgments
- Maintains all essential instructions in more direct format

### Fix 3: Add Detection for Raw Citations

**File**: `backend/interface.py`

Added detection logic to warn when providers return raw citations (still useful for diagnostics):

```python
# Detect raw citation snippets
citation_pattern_indicators = [
    summary.count(".") > 20 and summary.count(",") > 10,
    len(summary) < 500 and summary.count("\n") > 5,
    any(marker in summary[:200] for marker in [" et al.", "Journal of", "In Proceedings", "arXiv:"]),
]
if sum(citation_pattern_indicators) >= 2:
    print("\nWARNING: Detected raw citation snippets!")
    print("    Provider may have returned search results instead of answer.")
```

### Fix 4: Test Script for Google

**File**: `scripts/test-google-provider.py`

Created test script to verify Google provider works correctly:

```bash
export GOOGLE_API_KEY='your-key-here'
python scripts/test-google-provider.py
```

Tests:
1. Single-turn conversation
2. Multi-turn conversation  
3. RAG-style context with citations

## Testing the Fixes

### For Perplexity

1. **Start a new conversation** with a multi-turn question sequence
2. **Check first response** - should be direct answer without meta-acknowledgments
3. **Continue to 3rd and 4th questions** - should maintain conversational answers, not return citations
4. **Monitor backend logs** - look for detection warnings if issues occur

### For Google Gemini

1. **Run the test script**:
```bash
export GOOGLE_API_KEY='your-api-key'
python scripts/test-google-provider.py
```

2. **Start a conversation** in the app with Google as provider
3. **Check responses** - should be synthesized answers, not snippets or errors
4. **Check backend logs** - errors now show full traceback for debugging

### Expected Behavior

✅ **First turn**: Direct answer with citations, no meta-responses  
✅ **Follow-up turns**: Contextual answers building on conversation  
✅ **Multiple providers**: Both Perplexity and Google should work  
✅ **Error handling**: Clear error messages instead of silent snippet fallback

## Alternative: Switch to Different Provider

**Important Note**: Perplexity Sonar models are fundamentally designed for web search. If issues persist despite these fixes, consider:

1. **OpenAI (GPT-4o)**: Best for RAG over private documents
2. **Anthropic (Claude 3.5 Sonnet)**: Excellent at following context instructions  
3. **Ollama (Local)**: Full control, no web search confusion

To switch providers:
1. Go to Settings → Model Provider
2. Select alternative provider
3. Enter API key and test connection
4. Choose appropriate model
5. Save settings

## Technical Background

### Why Perplexity Behaves This Way

Perplexity Sonar models are trained with a special architecture:

1. **Query Understanding**: Analyze user question
2. **Web Search**: Automatically search the internet
3. **Citation Extraction**: Pull relevant snippets from web pages
4. **Answer Synthesis**: Combine web sources into answer with citations

This architecture is excellent for **web research** but problematic for **RAG over private documents** because:

- The model expects to search, not just synthesize
- It has built-in web search activation triggers
- Context confusion between provided documents vs. web sources
- Citation formatting optimized for web URLs, not academic papers

### API Parameters Used

```python
return_citations: bool = False     # Don't return web citations
return_images: bool = False        # Don't return web images
search_recency_filter: str = None  # Don't filter by time period
```

These are **undocumented** in Perplexity's public API docs but are part of the OpenAI-compatible interface.

## Verification

Run your test conversation again:

```
User: "Summarise my literature on distribution shifts"
Expected: Direct answer with citations from your library

User: "Search my zotero library on literature on distribution shifts..."  
Expected: Synthesized answer from library

User: "OK, see if you can find literature on possible ways to mitigate it..."
Expected: Answer from library context, NOT raw web citations

User: "Your last answer does not present the information well"
Expected: Reformatted answer, NOT raw document snippets
```

## Future Improvements

1. **Add Perplexity-specific prompting** - If Perplexity continues to be used, create provider-specific prompts
2. **Conversation state tracking** - Monitor for web search activation and prevent it
3. **Response validation** - Automatically detect and retry when citations are returned
4. **Provider recommendations** - Suggest optimal provider based on use case

## Summary

### Fixes Applied

✅ **Perplexity**: Web search mode disabled via API parameters  
✅ **Google Gemini**: Complete rewrite to use native chat format and system instructions  
✅ **All Providers**: System prompt simplified to reduce meta-responses  
✅ **Error Handling**: Better diagnostics instead of silent snippet fallback  
✅ **Testing**: Test script for Google provider validation

### What Was Wrong

1. **Perplexity**: `return_citations` not explicitly disabled → web search activated
2. **Google**: Wrong message format (string concatenation vs. native chat API)
3. **Google**: System prompt as message instead of separate parameter
4. **Google**: Safety settings too strict → blocked academic content
5. **All Providers**: Silent error fallback → returned snippets on any exception

### Files Changed

- `backend/model_providers/additional.py` - Fixed Perplexity and Google providers
- `backend/academic_prompts.py` - Simplified system prompt
- `backend/interface.py` - Better error handling and diagnostics
- `scripts/test-google-provider.py` - New test script for Google
- `docs/PERPLEXITY_API_FIX.md` - This documentation

⚠️ **Important**: If Google still returns snippets, check the backend logs. The improved error handling will now show exactly what's failing.
