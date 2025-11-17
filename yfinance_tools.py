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
    Search for recent news about a stock or company.

    Parameters
    ----------
    query : str
        Stock ticker or company name (e.g., "AAPL", "TSLA").
    news_count : int, optional
        Maximum number of news items to fetch (default: 8).

    Returns
    -------
    list[SearchResult]
        A list of news items with uuid, title, publisher, link, and publish time.
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
    Get trailing twelve-month (TTM) financials for a ticker.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol (e.g., "AAPL", "TSLA").

    Returns
    -------
    TickerInfo
        Object containing the symbol and a dict of TTM financials.
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


class FullStockInfo(BaseModel):
    symbol: str
    info: dict


@function_tool
@router.get("/stock_info/{ticker}")
def stock_info(ticker: str) -> FullStockInfo:
    """Get full raw yfinance `info` dictionary for a ticker.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol (e.g., "AAPL", "TSLA").

    Returns
    -------
    FullStockInfo
        Object containing the symbol and the entire `info` dict from yfinance.
        If retrieval fails, returns an empty dict for `info`.
    """
    logger.info("stock_info() called with ticker=%s", ticker)
    try:
        yf_ticker: YFTicker = yfinance.Ticker(ticker)
        info = yf_ticker.info  # This is a dict with many metadata fields
    except Exception:
        logger.error("Failed to retrieve stock info for ticker=%s", ticker)
        info = {}

    logger.info("Retrieved %d info fields for ticker=%s", len(info), ticker)
    return FullStockInfo(symbol=ticker, info=info)
