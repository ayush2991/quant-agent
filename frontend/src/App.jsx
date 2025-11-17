import React, { useState } from "react";

const DEFAULT_QUERY = "Analyze AAPL stock performance over the last 12 months.";
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function App() {
  const [message, setMessage] = useState(DEFAULT_QUERY);
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!message.trim() || loading) return;
    
    setLoading(true);
    setError(null);
    setOutput("");

    try {
      const query = encodeURIComponent(message.trim());
      const response = await fetch(`${BACKEND_URL}/ask?message=${query}`);
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || response.statusText || "Request failed");
      } else if (data.error) {
        setError(data.error);
      } else {
        setOutput(data.response ?? JSON.stringify(data, null, 2));
      }
    } catch (error) {
      setError(error.message || String(error));
    } finally {
      setLoading(false);
    }
  };

  const isSubmitDisabled = loading || !message.trim();

  const renderOutput = () => {
    if (error) {
      return (
        <pre id="output" className="error" aria-live="polite">
          {error}
        </pre>
      );
    }
    
    if (output) {
      return (
        <pre id="output" aria-live="polite">
          {output}
        </pre>
      );
    }
    
    return null;
  };

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
            disabled={loading}
          />
          <button type="submit" disabled={isSubmitDisabled}>
            {loading ? (
              <span className="loading-text">
                <span className="spinner"></span>
                Analyzing...
              </span>
            ) : (
              "Ask Agent"
            )}
          </button>
        </form>

        {loading && !error && !output && (
          <div className="loading-message">
            <div className="pulse"></div>
            <p>Processing your request...</p>
          </div>
        )}

        {renderOutput()}
      </main>
    </div>
  );
}
