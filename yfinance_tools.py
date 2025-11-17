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
@router.get("/news")
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


@function_tool
@router.get("/stock")
def stock(ticker: str) -> dict:
    """
    Get basic stock information for a ticker.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol (e.g., "AAPL", "TSLA").

    Returns
    -------
    dict
        A dictionary containing basic stock information such as info, dividends, and splits.
    """
    logger.info("stock() called with ticker=%s", ticker)
    try:
        yf_ticker: YFTicker = yfinance.Ticker(ticker)
        stock_info = {
            "info": yf_ticker.info,
            "dividends": yf_ticker.dividends.to_dict(),
            "splits": yf_ticker.splits.to_dict(),
        }
    except Exception:
        logger.error("Failed to retrieve stock info for ticker=%s", ticker)
        stock_info = {}

    logger.info("Retrieved stock info for ticker=%s", ticker)
    return stock_info


@function_tool
@router.get("/financials")
def financials(ticker: str) -> dict:
    """
    Get financial statements for a ticker.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol (e.g., "AAPL", "TSLA").

    Returns
    -------
    dict
        A dictionary containing financial statements such as income statement,
        balance sheet, cash flow, calendar, and earnings dates.
    """
    logger.info("financials() called with ticker=%s", ticker)
    try:
        yf_ticker: YFTicker = yfinance.Ticker(ticker)
        financials_data = {
            "income_stmt": yf_ticker.get_income_stmt(as_dict=True, pretty=True),
            "quarterly_income_stmt": yf_ticker.quarterly_income_stmt.to_dict(),
            "ttm_income_stmt": yf_ticker.ttm_income_stmt.to_dict(),
            "balance_sheet": yf_ticker.get_balance_sheet(as_dict=True, pretty=True),
            "cashflow": yf_ticker.get_cashflow(as_dict=True, pretty=True),
            "quarterly_cashflow": yf_ticker.quarterly_cashflow.to_dict(),
            "ttm_cashflow": yf_ticker.ttm_cashflow.to_dict(),
            "calendar": yf_ticker.calendar,
            "earnings_dates": yf_ticker.get_earnings_dates().to_dict(),
        }
    except Exception:
        logger.error("Failed to retrieve financials for ticker=%s", ticker)
        financials_data = {}

    logger.info("Retrieved financial statements for ticker=%s", ticker)
    return financials_data


@function_tool
@router.get("/analysis_and_holdings")
def analysis_and_holdings(ticker: str) -> dict:
    """
    Get analyst recommendations and major holders for a ticker.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol (e.g., "AAPL", "TSLA").

    Returns
    -------
    dict
        A dictionary containing analyst recommendations, major holders,
        analyst price targets, earnings estimates, revenue estimates,
        earnings history, EPS trend, growth estimates, and insider purchases.
    """
    logger.info("analysis_and_holdings() called with ticker=%s", ticker)
    try:
        yf_ticker: YFTicker = yfinance.Ticker(ticker)
        data = {
            "analyst_recommendations": yf_ticker.recommendations.to_dict(),
            "major_holders": yf_ticker.major_holders.to_dict(),
            "analyst_price_targets": yf_ticker.get_analyst_price_targets(),
            "earnings_estimate": yf_ticker.earnings_estimate.to_dict(),
            "revenue_estimate": yf_ticker.revenue_estimate.to_dict(),
            "eanrings_history": yf_ticker.earnings_history.to_dict(),
            "eps_trend": yf_ticker.eps_trend.to_dict(),
            "growth_estimates": yf_ticker.growth_estimates.to_dict(),
            "insider_purchases": yf_ticker.insider_purchases.to_dict(),
        }
    except Exception:
        logger.error("Failed to retrieve analysis and holdings for ticker=%s", ticker)
        data = {}

    logger.info("Retrieved analysis and holdings for ticker=%s", ticker)
    return data
