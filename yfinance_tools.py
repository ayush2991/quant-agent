import yfinance
from yfinance import Search as YFSearch, Ticker as YFTicker
import logging
from pydantic import BaseModel
from fastapi import APIRouter
from agents import function_tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/debug", tags=["debug"])


class SearchResult(BaseModel):
    uuid: str
    title: str
    publisher: str
    link: str
    providerPublishTime: int


@function_tool
@router.get("/news/{query}")
def news(query: str, news_count: int = 8) -> list[SearchResult]:
    """
    Search for news and summaries about a stock.
    - **query**: The stock ticker or company name to search for. eg: "AAPL" or "TSLA"
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


class TickerInfo(BaseModel):
    symbol: str
    ttm_financials: dict


@function_tool
@router.get("/ticker/{ticker}")
def ticker_data(ticker: str) -> TickerInfo:
    """
    Get ttm financials for a given stock ticker.
    Args:
        ticker (str): The stock ticker symbol. eg: "AAPL" or "TSLA"
    Returns:
        dict: A dictionary containing ttm financials.
    """
    logger.info("ticker_data() called with ticker=%s", ticker)
    try:
        yf_ticker: YFTicker = yfinance.Ticker(ticker)
        ttm_financials = yf_ticker.ttm_financials.to_dict()
    except Exception:
        logger.error("Failed to retrieve data for ticker=%s", ticker)
        return {}

    ticker_info = TickerInfo(
        symbol=ticker,
        ttm_financials=ttm_financials,
    )
    logger.info("Retrieved data for ticker=%s", ticker)
    return ticker_info
