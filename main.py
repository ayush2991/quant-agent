import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner
from yfinance_tools import router as yfinance_router, news, ticker_data
from web_search_tools import router as web_search_router, web_search
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = OpenAI()

app = FastAPI()
app.include_router(yfinance_router)
app.include_router(web_search_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = Agent(
    name="quant-agent",
    instructions="""You are a helpful quantitative trading assistant with expertise in financial markets, stocks, and trading strategies.

Your capabilities:
- Retrieve recent news about stocks and companies
- Fetch financial data and TTM (trailing twelve-month) financials for tickers
- Search the web for current market information and trading insights

Guidelines:
- Provide clear, concise, and data-driven responses
- When analyzing stocks, consider both fundamental data and recent news
- Always cite your sources when referencing news or web search results
- Be objective and highlight both opportunities and risks
- Each tool should be invoked at most once per query - gather all necessary information efficiently

Important: Use each tool only once. Plan your information gathering carefully before making tool calls.""",
    model="gpt-5-nano",
    tools=[news, ticker_data, web_search],
)


@app.get("/ask")
async def ask(message: str):
    """
    Ask the Quant Agent a question.

    Parameters
    ----------
    message : str
        The user prompt or question.

    Returns
    -------
    dict
        JSON with key 'response' containing the agent's final output, or 'error' on failure.
    """
    logger.info(f"Incoming request: message='{message}'")
    try:
        result = await Runner.run(agent, message)
        logger.info("Agent response generated successfully")
        logger.debug(f"Agent response: {result.final_output}")
        return {"response": result.final_output}
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return {"error": str(e)}


@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns
    -------
    dict
        JSON indicating service status.
    """
    logger.debug("Health check")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Quant Agent server on 0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="warning")
