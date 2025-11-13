import asyncio
import logging
from fastapi import FastAPI
from openai import OpenAI
from agents import Agent, Runner
import uvicorn

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
client = OpenAI()

agent = Agent(
    name="quant-agent",
    instructions="You are a helpful quantitative trading assistant.",
    model="gpt-5-nano",
)


@app.get("/chat")
async def chat(message: str):
    logger.info(f"Incoming request: message='{message}'")
    try:
        result = await Runner.run(agent, message)
        logger.debug(f"Agent result: {result.final_output}")
        return {"response": result.final_output}
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return {"error": str(e)}


@app.get("/health")
def health():
    logger.debug("Health check")
    return {"status": "ok"}


if __name__ == "__main__":
    logger.info("Starting Quant Agent server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
