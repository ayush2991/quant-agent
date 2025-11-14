import yfinance
from yfinance import Search as YFSearch
import logging
from agents import function_tool
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SearchResult(BaseModel):
    uuid: str
    title: str
    publisher: str
    link: str
    providerPublishTime: int


@function_tool
def news(query: str, news_count: int = 8) -> list[SearchResult]:
    """
    Search for news and summaries about a stock.
    Args:
        query (str): The stock ticker or company name to search for. eg: "AAPL" or "TSLA"
        news_count (int): Number of news items to include in the summary. Default is 8.
    Returns:
        list[SearchResult]: A list of SearchResult objects.
    """
    logger.info("news() called with query=%s news_count=%d", query, news_count)
    try:
        search_results: YFSearch = yfinance.Search(query=query, news_count=news_count)
    except Exception:
        logger.error("Failed to perform yfinance.Search for query=%s", query)
        return []

    news_results = []
    try:
        for search_result in getattr(search_results, "news", []):
            news_results.append(
                SearchResult(
                    uuid=search_result["uuid"],
                    title=search_result["title"],
                    publisher=search_result.get("publisher", ""),
                    link=search_result.get("link", ""),
                    providerPublishTime=search_result.get("providerPublishTime", 0),
                )
            )
    except Exception:
        logger.error("Error while parsing search results for query=%s", query)
        return []

    logger.info("Found %d news items for query=%s", len(news_results), query)
    return news_results
