"""
Extract metadata filters from natural language queries using an LLM.

The extractor asks the active model to identify any explicitly-stated
metadata constraints (author, title, year range, item type, tags, collections)
and returns them as a structured dict that is fed directly into
build_metadata_where_clause() — the same path used by manual Scope-panel filters.
"""

import re
import json
import logging
from typing import Dict, Any, Optional

from backend.model_providers.base import Message

logger = logging.getLogger(__name__)

# Empty-filters sentinel — returned whenever extraction produces nothing.
_EMPTY: Dict[str, Any] = {
    "year_min": None,
    "year_max": None,
    "tags": [],
    "collections": [],
    "author": None,
    "title": None,
    "item_types": [],
    "has_filters": False,
}


class MetadataExtractor:
    """Extract structured metadata filters from natural language queries via LLM."""

    #: Prompt sent to the model. Kept as a class attribute so it can be
    #: inspected / overridden in tests.
    EXTRACTION_PROMPT = """\
Extract structured metadata filters from this academic library search query.
Return JSON with these fields (use null / empty list when the field is absent):

- year_min   : earliest year as integer (e.g. 2018), or null
- year_max   : latest year as integer (e.g. 2023), or null
- tags       : list of topic/keyword tags EXPLICITLY mentioned (e.g. ["NLP", "deep learning"])
- collections: list of Zotero collection names EXPLICITLY mentioned (e.g. ["PhD Research"])
- author     : last name or full name of a specific author EXPLICITLY mentioned, or null
- title      : title fragment of a specific paper/book/thesis EXPLICITLY mentioned, or null
- item_types : list of document types EXPLICITLY mentioned — use only these Zotero names:
               "journalArticle", "book", "bookSection", "conferencePaper", "thesis",
               "preprint", "webpage", "report", "presentation", "manuscript"

Rules:
- Only extract what is EXPLICITLY stated. Do not infer topics from the question subject.
  Example: "What does Berlant argue?" → no tags, no author (just a rhetorical question)
  Example: "Papers by Berlant about optimism" → author: "Berlant", tags: ["optimism"]
- "thesis", "dissertation", "master's thesis", "PhD thesis" → item_types: ["thesis"]
- Author names: extract only if the query asks for a specific person's work, not just mentions a name.
- "recent" / "latest" alone is not a year filter.

Query: "{query}"

Return ONLY valid JSON, no explanation:"""

    def __init__(self, provider_manager=None):
        self.provider_manager = provider_manager

    def extract_filters(self, query: str) -> Dict[str, Any]:
        """
        Extract metadata filters from *query* using the LLM.

        Returns a dict with keys: year_min, year_max, tags, collections,
        author, title, item_types, has_filters.  When no provider_manager is
        configured (or the LLM call fails), returns an empty-filters dict so
        the caller can safely proceed without any metadata constraint.
        """
        if not self.provider_manager:
            logger.debug("No provider_manager — skipping metadata extraction")
            return dict(_EMPTY)

        try:
            filters = self._extract_with_llm(query)
            logger.debug(f"LLM-extracted filters: {filters}")
            return filters
        except Exception as e:
            logger.warning(f"Metadata extraction failed, returning empty filters: {e}")
            return dict(_EMPTY)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _extract_with_llm(self, query: str) -> Dict[str, Any]:
        if self.provider_manager is None:
            raise ValueError("No provider_manager available for LLM extraction")

        prompt = self.EXTRACTION_PROMPT.format(query=query)

        response = self.provider_manager.chat(
            messages=[Message(role="user", content=prompt)],
            temperature=0.0,
            max_tokens=200,
        )

        content = response.content

        # Strip optional markdown code fences
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

        extracted = json.loads(content)

        filters: Dict[str, Any] = {
            "year_min":    extracted.get("year_min"),
            "year_max":    extracted.get("year_max"),
            "tags":        extracted.get("tags") or [],
            "collections": extracted.get("collections") or [],
            "author":      extracted.get("author") or None,
            "title":       extracted.get("title") or None,
            "item_types":  extracted.get("item_types") or [],
            "has_filters": False,
        }

        if (filters["year_min"] or filters["year_max"] or
                filters["tags"] or filters["collections"] or
                filters["author"] or filters["title"] or filters["item_types"]):
            filters["has_filters"] = True

        return filters


# Convenience function used by interface.py
def extract_metadata_filters(query: str, provider_manager=None) -> Dict[str, Any]:
    """
    Extract metadata filters from *query* via LLM.

    Args:
        query: Natural language query
        provider_manager: Active ProviderManager (required for extraction)

    Returns:
        Dict with year_min, year_max, tags, collections, author, title,
        item_types, has_filters.  All fields present; has_filters=False
        means no actionable filter was found.
    """
    return MetadataExtractor(provider_manager).extract_filters(query)
