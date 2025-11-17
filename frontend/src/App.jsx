import React, { useState } from "react";

export default function App() {
  const [message, setMessage] = useState("Analyze AAPL stock performance over the last 12 months.");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e?.preventDefault();
    if (!message.trim() || loading) return;
    
    setLoading(true);
    setError(null);
    setOutput("");
    try {
      const q = encodeURIComponent(message.trim());
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/ask?message=${q}`);
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
        <form className="controls" onSubmit={handleSubmit}>
          <input
            type="text"
            aria-label="query"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="query-input"
            placeholder="Enter your query..."
          />
          <button type="submit" disabled={loading || !message.trim()}>
            {loading ? "Loading…" : "Ask Agent"}
          </button>
        </form>

        {error ? (
          <pre id="output" className="error" aria-live="polite">{error}</pre>
        ) : (
          <pre id="output" aria-live="polite">{output}</pre>
        )}
      </main>
    </div>
  );
}
