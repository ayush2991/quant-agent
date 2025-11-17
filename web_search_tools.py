import os
import logging
import requests
from pydantic import BaseModel
from fastapi import APIRouter
from agents import function_tool
from diskcache import Cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/debug", tags=["debug"])

# Initialize disk cache with 24-hour TTL
cache = Cache(".cache/web_search", size_limit=100 * 1024 * 1024)  # 100MB limit


class WebSearchResult(BaseModel):
    title: str
    url: str
    description: str
    age: str


@function_tool
@router.get("/search")
def web_search(
    query: str, count: int = 10, freshness: str = "pw"
) -> list[WebSearchResult]:
    """
    Search the web using Brave Search API.

    Parameters
    ----------
    query : str
        Search query string.
    count : int, optional
        Maximum number of search results to return (default: 10).
    freshness: str, optional
        Filter results by freshness.
        Valid values: "pd" --> last 24 hours, "pw" --> last week, "pm" --> last month.
        (default: "pw")


    Returns
    -------
    list[WebSearchResult]
        A list of search results with title, url, and description.
    """
    logger.info("web_search() called with query=%s count=%d", query, count)

    # Create cache key
    cache_key = f"search:{query}:{count}:{freshness}"

    # Check cache
    cached_results = cache.get(cache_key)
    if cached_results is not None:
        logger.info("Cache hit for query=%s", query)
        return [WebSearchResult(**result) for result in cached_results]

    logger.info("Cache miss - performing web search for query=%s", query)

    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        logger.error("BRAVE_API_KEY environment variable not set")
        return []

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }
    params = {
        "q": query,
        "count": count,
        "freshness": freshness,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        search_results = []
        for result in data.get("web", {}).get("results", []):
            search_results.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "age": result.get("page_age", ""),
                }
            )

        # Cache results for 24 hours
        cache.set(cache_key, search_results, expire=86400)

        logger.info("Found %d search results for query=%s", len(search_results), query)
        return [WebSearchResult(**result) for result in search_results]
    except Exception as e:
        logger.error("Failed to perform web search for query=%s: %s", query, str(e))
        return []
