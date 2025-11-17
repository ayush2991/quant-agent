# Quant Agent - Learning Journey

## Overview

Built a quantitative analysis chatbot with a FastAPI backend, OpenAI agent tools, and a React frontend. The system answers finance questions by aggregating data from external sources (`yfinance`, Brave Search) and exposing pragmatic HTTP endpoints and agent-friendly tools.

## Backend (FastAPI) Learnings

- **Routers and Endpoint Design**: Grouped related endpoints with `APIRouter` (e.g., `prefix="/debug"`) to keep APIs modular and discoverable.
- **Query Parameters and Responses**: Implemented GET handlers that accept query params and return JSON-friendly dicts/lists. Avoided over-modeling when returning third-party API payloads.
- **Returning Raw JSON When Appropriate**: In `web_search_tools.py`, removed a Pydantic model and returned the raw Brave Search JSON. This preserved full fidelity of the upstream API and reduced maintenance.
- **Error Handling and Logging**: Used structured logging to trace inputs and outcomes, logging errors without crashing endpoints. Returned empty dict/list on failures to keep clients resilient.
- **Async Consideration**: Considered `async` routes, but current endpoints are synchronous since the heavy work is I/O via libraries that already block; caching mitigates most latency.

## Agent Tools (OpenAI Agents) Learnings

- **Function Tools Pattern**: Decorated functions with `@function_tool` to expose clear, callable tools for the agent. This enforces narrow, testable contracts and makes tools reusable via HTTP (`/debug/*`) and by the agent runtime.
- **Tool Boundaries and Inputs**: Kept tool signatures simple (primitives, small enums) to make invocation robust. Preferred returning serializable dicts/lists over custom objects for compatibility.
- **Observability**: Each tool logs inputs, cache hits/misses, and failure paths to aid iterative agent prompt/tool design.

## Data Integrations Learnings

- **YFinance Integration**:
  - Accessed news, stock info, financials, analysis, and holdings via `yfinance.Ticker` and helper methods.
  - Converted `pandas` objects to serializable forms with `.to_dict()` before returning or caching.
  - Avoided caching the `Ticker` instance itself because it includes non-picklable internals (e.g., `_thread.RLock`). Prefer caching the derived, serializable results instead.
- **Brave Search Integration**:
  - Called the Brave Search API with `BRAVE_API_KEY`; returned the raw JSON for flexibility.
  - Cached full API responses to minimize external calls while debugging.

## Caching Strategy Learnings

- **Disk-Based Endpoint Caching**: Used `diskcache` to cache final responses from endpoints in `yfinance_tools.py`:
  - `news`: list of news dicts (TTL ~5m)
  - `stock`: `stock_info` dict (TTL ~10m)
  - `financials`: `financials_data` dict (TTL ~30m)
  - `analysis_and_holdings`: analysis/holdings dict (TTL ~30m)
- **Serializable-Only Caching**: Cached only dicts/lists/primitives. Attempting to cache `yfinance.Ticker` raised a pickle error due to locks; lesson learned: cache data, not complex object graphs.
- **Cache Keys and Safety**: Keys encode inputs (e.g., ticker, query, counts). Reads/writes wrapped in try/except so cache issues never break requests.

## Frontend (React + Vite) Learnings

- **State and UX**: Implemented a controlled input (`message`), result `output`, `loading`, and `error` states. Disabled the submit button during requests for clear UX.
- **A11y and Rendering**: Rendered responses in a `<pre>` and used `aria-live="polite"` so screen readers announce updates.
- **Networking**: The app currently fetches `http://localhost:8000/ask` directly. A Vite dev proxy exists to forward `/api/*` to the backend; switching to a relative `/api/ask` path would leverage it and simplify environment switching.
- **Dev/Prod Routing**: Learned that Firebase Hosting rewrites `/api/**` to Cloud Run in production (`firebase.json`). For local dev, the Vite proxy or explicit `localhost` base URL avoids conflicts with the production rewrite.

## DevOps & Environment Learnings

- **Firebase Hosting → Cloud Run**: Useful production setup, but it can mask local testing if the frontend is served via Firebase emulators. Distinguish local dev (Vite) from production (Hosting) and use a proxy or explicit base URL for `/api`.
- **Secrets and Env Vars**: External APIs (e.g., Brave Search) require env vars like `BRAVE_API_KEY`. Documenting and validating these early avoids confusing failures.

## Pitfalls and Fixes

- Tried caching `yfinance.Ticker` → encountered `TypeError: cannot pickle '_thread.RLock'` from diskcache. Fixed by caching only serializable outputs.
- Firebase rewrite for `/api/**` pointed at Cloud Run, blocking local FastAPI testing when serving via Hosting. Fixed local dev by using Vite proxy and/or explicit `http://localhost:8000` in fetch.
- Over-modeling responses with Pydantic made integration brittle; returning raw JSON (Brave Search) simplified usage and reduced code churn.

## What I’d Do Next

- Make cache TTLs adjustable via environment variables and centralize cache config.
- Normalize large DataFrames to compact record lists for smaller cache size.
- Switch frontend fetches to `/api/ask` and rely on the Vite proxy for cleaner dev/prod parity.
