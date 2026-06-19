"""Web search tool backed by the Tavily API.

The research agent uses this to gather news, financials and recent
developments about a company.
"""

import logging
import time

from tavily import TavilyClient

from app.config import settings

_client = TavilyClient(api_key=settings.tavily_api_key.get_secret_value())


logger = logging.getLogger(__name__)

def tavily_search(query: str, max_results: int | None = None) -> list[dict]:
    """Run a web search and return a list of result dicts.

    Each result contains at least `title`, `url` and `content` keys.
    """
    results = max_results or settings.max_search_results
    
    max_retries = 3
    base_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            response = _client.search(
                query=query,
                max_results=results,
                search_depth="advanced",
            )
            return response.get("results", [])
        except Exception as e:
            logger.warning(f"Tavily search failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                logger.error("Tavily search exhausted retries. Returning fallback result.")
                return [{
                    "title": "Search Failed", 
                    "url": "", 
                    "content": f"[SYSTEM: The web search failed due to an error: {e}. You must rely on existing context.]"
                }]
            time.sleep(base_delay * (2 ** attempt))
            
    return []
