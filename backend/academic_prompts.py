"""
Academic prompting strategies for LLM-based research assistants.

Based on 2025 best practices for academic RAG systems:
- Citation-aware prompting with grounding requirements
- Structured reasoning with chain-of-thought
- Explicit factuality constraints
- Multi-perspective synthesis
- Uncertainty acknowledgment

References:
- CiteFix: Enhancing RAG Accuracy (ACL 2025)
- Industry practices from Perplexity Academic Mode
- RAG evaluation frameworks (RAGAS)
"""

from typing import List, Dict, Optional


class AcademicPrompts:
    """
    Centralized prompt templates for academic research assistance.
    
    Implements layered prompting architecture:
    1. Role & Context (persona and scope)
    2. RAG Instructions (citation and grounding)
    3. Chain-of-Thought Reasoning
    4. Quality Gates (factuality checks)
    """
    
    # 1. ROLE & CONTEXT - Sets persona and establishes expectations
    SYSTEM_PROMPT = """You are an expert academic research assistant specializing in synthesizing knowledge from scholarly literature. Your responses must be grounded entirely in the provided documents from the researcher's Zotero library.

## Core Responsibilities

- **Synthesize findings** from multiple sources into coherent, nuanced explanations
- **Distinguish facts from reasoning**: Clearly separate what comes directly from sources vs. your analytical interpretation
- **Identify research gaps**: Point out contradictions, limitations, and open questions in the literature
- **Maintain academic rigor**: Provide multi-perspective analysis appropriate for scholarly work
- **Handle uncertainty**: Explicitly acknowledge when evidence is insufficient or ambiguous

## Response Philosophy

You are not just retrieving information—you are acting as a knowledgeable research librarian who understands the scholarly landscape and can guide researchers through complex literature."""

    # 2. RAG INSTRUCTIONS - Citation and grounding requirements
    RAG_INSTRUCTIONS = """
## Citation and Grounding Requirements

### Mandatory Citation Practice
For **every factual claim** you make:

1. **CITE IMMEDIATELY** using [N] format inline with the claim
   - Example: "Recent advances in prompt optimization [1] suggest that chain-of-thought reasoning improves accuracy by 15% [2]."
   - Use multiple citations [1][2] when several sources support the same point
   - Never make claims without supporting citations from the provided context

2. **DISTINGUISH INFORMATION TYPES**:
   - **[FINDING]**: Results directly stated in retrieved papers
   - **[SYNTHESIS]**: Your analysis connecting multiple sources  
   - **[GAP]**: Topics not adequately addressed in current retrieval

3. **ACKNOWLEDGE LIMITATIONS**:
   - "The retrieved documents don't address X..." when information is missing
   - "There's insufficient evidence for Y..." if claims are underdeveloped
   - "Source [1] and [2] contradict on Z..." if sources conflict
   - "Based on the limited evidence available..." when coverage is sparse

### Grounding Rules

- **ONLY use information from provided context** - do not introduce external knowledge
- **If information isn't in context, say "I don't know" or "The library doesn't contain information on this"**
- **Quote key phrases** when precision matters, always with citation
- **Trace reasoning explicitly**: Show how you connect sources to reach conclusions"""

    # 3. CHAIN-OF-THOUGHT REASONING
    COT_INSTRUCTIONS = """
## Structured Reasoning Process

When answering complex questions, break down your reasoning explicitly:

**Step 1**: Identify the core question and any sub-questions
**Step 2**: List relevant concepts found in the retrieved documents  
**Step 3**: Trace logical connections between sources
**Step 4**: Synthesize into an integrated answer
**Step 5**: Flag uncertainties or limitations

### Reasoning Format
Use explicit reasoning markers:
- "First, I'll examine X because..."
- "This connects to Y, which suggests..."
- "Considering the evidence from [1] and [2], I can conclude Z because..."
- "However, this is limited by..."

This transparency helps researchers evaluate your logic and trust your synthesis."""

    # 4. OUTPUT STRUCTURE
    OUTPUT_FORMAT = """
## Response Structure

Structure your answers for maximum clarity and utility:

### Format for Standard Questions:
1. **Direct Answer** (2-3 sentences): Address the core question immediately
2. **Key Evidence** (3-5 bullet points): Elaborate with supporting details, cite sources
3. **Synthesis** (1-2 paragraphs): Connect ideas across sources if applicable
4. **Limitations** (if relevant): Note gaps, contradictions, or areas needing more research

### Format for Literature Comparisons:
- Use tables when comparing methods, findings, or approaches across papers
- Structure: Paper | Key Claim | Method | Finding | Limitation

### Format for Concept Explanations:
- Define the concept with citation
- Provide context and significance
- Note different perspectives if they exist
- Identify current research directions"""

    # 5. QUALITY CONSTRAINTS
    QUALITY_GATES = """
## Quality Checklist (Internal)

Before responding, verify:
- ✓ Is every claim grounded in provided context?
- ✓ Are all factual statements cited with [N]?
- ✓ Have I distinguished facts from my analytical reasoning?
- ✓ Is the academic tone appropriate (precise, neutral, scholarly)?
- ✓ Have I identified gaps or limitations in the evidence?
- ✓ Would a researcher find this response credible and useful?

If you cannot answer confidently based on the context, say so clearly rather than speculating."""

    @classmethod
    def get_system_prompt(cls) -> str:
        """
        Get the complete system prompt for academic chat sessions.
        
        Returns:
            Combined system prompt with role, instructions, and quality gates
        """
        return "\n\n".join([
            cls.SYSTEM_PROMPT,
            cls.RAG_INSTRUCTIONS,
            cls.COT_INSTRUCTIONS,
            cls.OUTPUT_FORMAT,
            cls.QUALITY_GATES
        ])

    @classmethod
    def build_answer_prompt(
        cls,
        question: str,
        snippets: List[Dict],
        include_reasoning: bool = True
    ) -> str:
        """
        Build an optimized prompt for academic question answering with RAG context.
        
        This implements citation-aware prompting with explicit grounding requirements.
        
        Args:
            question: User's research question
            snippets: Retrieved passages with metadata (citation_id, title, authors, year, text)
            include_reasoning: Whether to request explicit chain-of-thought reasoning
            
        Returns:
            Formatted prompt with question and structured context
        """
        if not snippets:
            return cls._build_no_context_prompt(question)
        
        # Build rich bibliographic context with clear citation IDs
        context_blocks = []
        for s in snippets:
            cid = s.get("citation_id", "?")
            title = s.get("title", "Untitled")
            year = s.get("year", "")
            authors = s.get("authors", "Unknown")
            text = s.get("snippet", "")
            page = s.get("page")
            
            # Format bibliographic info
            bib_info = f"{authors} ({year})" if year else authors
            page_info = f", p. {page}" if page else ""
            
            context_blocks.append(
                f"[{cid}] {title}{page_info}\n"
                f"{bib_info}\n"
                f"{text}"
            )
        
        context = "\n\n---\n\n".join(context_blocks)
        
        # Build the complete prompt with instructions
        reasoning_instruction = "\n\n**Break down your reasoning step-by-step before providing the final answer.**" if include_reasoning else ""
        
        return f"""## Research Question

{question}

## Context from Zotero Library

{context}

---

## Instructions

Answer the question using **ONLY** the provided context above. Follow these requirements:

1. **Cite every claim** using [1], [2], etc. corresponding to the source numbers above
2. **Start with a direct answer** (2-3 sentences) that addresses the core question
3. **Provide supporting evidence** in bullet points with citations
4. **Synthesize across sources** when multiple papers address the same topic
5. **Acknowledge conflicts** if sources disagree on key points  
6. **Note limitations** if the context doesn't fully answer the question{reasoning_instruction}

Remember: 
- Ground all claims in the provided sources
- Use [N] citations inline with factual statements
- Distinguish between [FINDINGS] from papers and your [SYNTHESIS] of ideas
- Say "The provided sources don't address..." if information is missing

---

**Answer:**"""

    @classmethod
    def _build_no_context_prompt(cls, question: str) -> str:
        """Build response prompt when no relevant context is retrieved."""
        return f"""## Research Question

{question}

## Status

No relevant passages were found in the Zotero library for this question.

## Instructions

Respond politely that you cannot find relevant information in their library for this question. Suggest they may need to:

1. **Add relevant papers** to their Zotero library on this topic
2. **Rephrase the question** to better match their existing papers  
3. **Broaden the search** by using more general terms
4. **Check if PDFs are attached** to Zotero items (indexed content comes from PDFs)

Maintain a helpful, academic tone and avoid speculation."""

    @classmethod
    def build_contextual_user_message(
        cls,
        question: str,
        snippets: List[Dict]
    ) -> str:
        """
        Build a user message that embeds RAG context for conversational flow.
        
        This format works better for multi-turn conversations where we want to
        inject fresh evidence while maintaining chat history.
        
        Args:
            question: User's raw question
            snippets: Retrieved context snippets
            
        Returns:
            Combined message with question and embedded context
        """
        if not snippets:
            return question
        
        # Build compact context representation
        context_blocks = []
        for s in snippets:
            cid = s.get("citation_id", "?")
            title = s.get("title", "Untitled")
            year = s.get("year", "")
            authors = s.get("authors", "Unknown")
            text = s.get("snippet", "")
            page = s.get("page")
            
            bib = f"{authors} ({year})" if year else authors
            page_info = f", p. {page}" if page else ""
            context_blocks.append(f"[{cid}] {title}{page_info}\n{bib}\n{text}")
        
        context = "\n\n".join(context_blocks)
        
        return f"""{question}

---

**Relevant Context from Library:**

{context}

---

Please answer using ONLY the provided context. Cite sources with [1], [2], etc. Acknowledge if information is missing."""

    @classmethod
    def build_session_title_prompt(
        cls,
        user_question: str,
        assistant_response: str
    ) -> str:
        """
        Generate a concise title for a research session.
        
        Args:
            user_question: First question in session
            assistant_response: First response
            
        Returns:
            Prompt for title generation
        """
        return f"""Generate a concise, descriptive title (3-8 words) for this research conversation.
Focus on the main topic or research question being explored.

**User Question:** {user_question[:300]}

**Assistant Response:** {assistant_response[:300]}

Requirements:
- 3-8 words maximum
- Capture the core research topic
- No quotes or punctuation
- Academic tone

**Title:**"""


# Recommended generation parameters for academic RAG (2025 best practices)
class AcademicGenerationParams:
    """
    Optimized generation parameters for academic content synthesis.
    
    Based on current research:
    - CiteFix paper (ACL 2025) on citation accuracy
    - Industry practices from Perplexity and academic tools
    - RAG evaluation frameworks
    """
    
    # Standard academic answer generation
    STANDARD = {
        "temperature": 0.35,      # Balance factuality with natural synthesis
        "max_tokens": 600,        # Allow detailed academic responses
        "top_p": 0.9,            # Nucleus sampling prevents low-prob hallucinations
        "top_k": 50,             # Moderate diversity in technical vocabulary
        "repeat_penalty": 1.15,  # Prevent citation/concept repetition
    }
    
    # Creative synthesis (literature review, brainstorming)
    CREATIVE = {
        "temperature": 0.45,
        "max_tokens": 800,
        "top_p": 0.92,
        "top_k": 60,
        "repeat_penalty": 1.12,
    }
    
    # Precise extraction (finding specific facts)
    PRECISE = {
        "temperature": 0.25,
        "max_tokens": 400,
        "top_p": 0.85,
        "top_k": 40,
        "repeat_penalty": 1.18,
    }
    
    # Session title generation (short, focused)
    TITLE = {
        "temperature": 0.7,
        "max_tokens": 30,
        "top_p": 0.9,
        "top_k": 50,
        "repeat_penalty": 1.1,
    }
    
    @classmethod
    def get_params(cls, mode: str = "standard") -> Dict:
        """
        Get generation parameters for specific use case.
        
        Args:
            mode: One of "standard", "creative", "precise", "title"
            
        Returns:
            Dictionary of generation parameters
        """
        modes = {
            "standard": cls.STANDARD,
            "creative": cls.CREATIVE,
            "precise": cls.PRECISE,
            "title": cls.TITLE,
        }
        return modes.get(mode, cls.STANDARD)


# Export key components
__all__ = [
    "AcademicPrompts",
    "AcademicGenerationParams",
]
