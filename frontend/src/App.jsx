import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

const DEFAULT_QUERY = "Is GOOG a good buy right now?";
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function App() {
  const [message, setMessage] = useState(DEFAULT_QUERY);
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const resultRef = useRef(null);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!message.trim() || loading) return;

    setLoading(true);
    setError(null);
    setOutput("");
    setShowResult(true);

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

  useEffect(() => {
    if (showResult && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [showResult]);

  const isSubmitDisabled = loading || !message.trim();

  return (
    <div className="app-container">
      <div className="background-glow"></div>

      <header className="app-header">
        <div className="logo">
          <i className="fa-solid fa-chart-line"></i>
          <span>Quant Agent</span>
        </div>
      </header>

      <main className="main-content">
        <div className="hero-section">
          <h1 className="hero-title">
            Market Intelligence <br />
            <span className="gradient-text">Reimagined</span>
          </h1>
          <p className="hero-subtitle">
            Advanced AI analysis for stocks, financials, and market trends.
          </p>
        </div>

        <div className="search-container">
          <form className="search-form" onSubmit={handleSubmit}>
            <div className="input-wrapper">
              <i className="fa-solid fa-magnifying-glass search-icon"></i>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="search-input"
                placeholder="Ask about any stock or market trend..."
                disabled={loading}
              />
              <button
                type="submit"
                className={`search-button ${loading ? 'loading' : ''}`}
                disabled={isSubmitDisabled}
              >
                {loading ? <i className="fa-solid fa-circle-notch fa-spin"></i> : <i className="fa-solid fa-arrow-right"></i>}
              </button>
            </div>
          </form>

          <div className="suggestions">
            <span>Try:</span>
            <button onClick={() => setMessage("Analyze NVDA earnings")}>NVDA Earnings</button>
            <button onClick={() => setMessage("Crypto market outlook")}>Crypto Outlook</button>
            <button onClick={() => setMessage("Compare AAPL and MSFT")}>AAPL vs MSFT</button>
          </div>
        </div>

        {(showResult || loading) && (
          <div className="result-section" ref={resultRef}>
            {loading && !output && !error && (
              <div className="loading-state">
                <div className="loader-pulse"></div>
                <p>Analyzing market data...</p>
              </div>
            )}

            {error && (
              <div className="error-card">
                <i className="fa-solid fa-circle-exclamation"></i>
                <p>{error}</p>
              </div>
            )}

            {output && (
              <div className="result-card fade-in">
                <div className="result-header">
                  <i className="fa-solid fa-robot"></i>
                  <span>Agent Analysis</span>
                </div>
                <div className="markdown-content">
                  <ReactMarkdown>{output}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
