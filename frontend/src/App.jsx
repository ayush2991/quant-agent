import React, { useState } from "react";

export default function App() {
  const [message, setMessage] = useState("Give me a one-line market summary.");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleFetch() {
    setLoading(true);
    setError(null);
    setOutput("");
    try {
      const q = encodeURIComponent(message || "");
      const res = await fetch(`http://localhost:8000/ask?message=${q}`);
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || res.statusText || "Request failed");
      } else if (data.error) {
        setError(data.error);
      } else {
        setOutput(data.response ?? JSON.stringify(data, null, 2));
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Quant Agent</h1>
      </header>
      <main>
        <div className="controls">
          <input
            aria-label="query"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="query-input"
          />
          <button id="fetch-btn" onClick={handleFetch} disabled={loading}>
            {loading ? "Loading…" : "Fetch sample data"}
          </button>
        </div>

        {error ? (
          <pre id="output" className="error" aria-live="polite">{error}</pre>
        ) : (
          <pre id="output" aria-live="polite">{output}</pre>
        )}
      </main>
    </div>
  );
}
