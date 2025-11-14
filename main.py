import logging
from fastapi import FastAPI
from openai import OpenAI
from agents import Agent, Runner
from yfinance_tools import news
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
agent = Agent(
    name="quant-agent",
    instructions="You are a helpful quantitative trading assistant.",
    model="gpt-5-nano",
    tools=[news],
)


@app.get("/ask")
async def ask(message: str):
    logger.info(f"Incoming request: message='{message}'")
    try:
        result = await Runner.run(agent, message)
        return {"response": result.final_output}
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return {"error": str(e)}


@app.get("/health")
def health():
    logger.debug("Health check")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Quant Agent server on 0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
