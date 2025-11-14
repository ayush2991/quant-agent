# Quant Agent - Learning Journey

## Completed Topics

- **FastAPI Server**: Built my first FastAPI server with basic routing and handlers
- **GET Handlers**: Implemented GET endpoints to handle query parameters and return JSON responses
- **FastAPI Logging**: Set up logging to monitor server activity and debug requests
- **OpenAI Agents SDK Basics**: Learned how to initialize and use OpenAI agents for intelligent responses
- **Async IO & Await**: Implemented asynchronous programming patterns for non-blocking operations
- **YFinance API & Tool Use**: Integrated yfinance's Search API and created a custom tool for fetching and formatting stock news

## Project Context

Building a quantitative analysis chatbot that answers financial and investment-related questions using FastAPI and OpenAI agents.

## React Frontend

- Controlled components: the frontend uses React's `useState` to manage the query input (`message`) and the returned `output`.
- Asynchronous requests: the UI performs an async `fetch` to the backend `/ask` endpoint, with `loading` and `error` state to reflect request progress and failures.
- Declarative rendering: the response (or error) is rendered into a `<pre>` block via React state rather than manipulating the DOM directly.
- Accessibility: the output area uses `aria-live="polite"` so screen readers are notified of updates.
- Error handling: the frontend parses JSON responses and displays friendly error messages when the request fails.
- UX details: a controlled input, a single button to trigger the request, and visual feedback (disabled button while loading) make the interface simple and clear.
