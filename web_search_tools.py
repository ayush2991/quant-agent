"""web_search_tools

Helpers for performing Brave web searches and caching results.

This module exposes a FastAPI router under the `/debug` prefix with a
`/search` endpoint that queries the Brave Search API and returns the raw
JSON response. Responses are cached on disk for 24 hours to reduce
external API calls during development.
"""

import os
import logging
import requests
from fastapi import APIRouter
from agents import function_tool
from diskcache import Cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/debug", tags=["debug"])

# Initialize disk cache with 24-hour TTL
cache = Cache(".cache/web_search", size_limit=100 * 1024 * 1024)  # 100MB limit


@function_tool
@router.get("/search")
def web_search(query: str, count: int = 10, freshness: str = "pw"):
    """Search the web using the Brave Search API.

    Parameters
    ----------
    query : str
        Search query string.
    count : int, optional
        Maximum number of search results to request (default: 10).
    freshness: str, optional
        Filter results by freshness. Valid values:
        - ``"pd"``: last 24 hours
        - ``"pw"``: last week (default)
        - ``"pm"``: last month

    Returns
    -------
    dict
        The raw JSON response parsed from the Brave Search API (the
        object returned by ``response.json()``). On success the response
        contains the ``web`` key with ``results`` (e.g. ``data['web']['results']``).

        The full API response is cached on disk for 24 hours under a key
        derived from ``query``, ``count``, and ``freshness``.

        If ``BRAVE_API_KEY`` is not set or an error occurs when calling
        the API, an empty dict (``{}``) is returned.
    """
    logger.info("web_search() called with query=%s count=%d", query, count)

    # Create cache key
    cache_key = f"search:{query}:{count}:{freshness}"

    # Check cache
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache hit for query=%s", query)
        return cached

    logger.info("Cache miss - performing web search for query=%s", query)

    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        logger.error("BRAVE_API_KEY environment variable not set")
        return {}

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

        # Cache the full API response for 24 hours
        cache.set(cache_key, data, expire=86400)

        logger.info("Returning API response for query=%s", query)
        return data
    except Exception as e:
        logger.error("Failed to perform web search for query=%s: %s", query, str(e))
        return {}
