# Quant Agent - User Guide

Welcome to the Quant Agent! This is an AI-powered assistant that answers questions about quantitative trading, market analysis, and investment strategies.

## Getting Started

The Quant Agent runs as a web service. Once running, you can chat with it by sending simple requests.

## How to Use

### Ask a Question

Send a request to the chat endpoint with your question:

```
GET http://localhost:8000/chat?message=What+is+a+moving+average
```

Replace `What+is+a+moving+average` with your question (use `+` for spaces).

### Example Questions

- "What is portfolio diversification?"
- "Explain the Sharpe ratio"
- "What are the risks of momentum trading?"
- "How do I analyze stock volatility?"

## Response Format

The agent returns a JSON response with the answer:

```json
{
  "response": "A moving average is a technical indicator that smooths price data by creating a constantly updated average price. It helps identify trends and support/resistance levels..."
}
```

## Health Check

To verify the service is running:

`GET http://localhost:8000/health`

Response:

```
{"status": "ok"}
```

## Using with cURL

If you have curl installed, you can test directly from command line:

```
curl "http://localhost:8000/chat?message=What+is+volatility"
```

## Tips

- Ask specific, clear questions for better answers
- The agent specializes in quantitative trading and market analysis
- Questions are answered independently (no conversation history yet)
- Keep questions concise for faster responses
