import React from "react";

export default function App() {
  return (
    <div className="app">
      <header>
        <h1>Quant Agent</h1>
      </header>
      <main>
        <button id="fetch-btn">Fetch sample data</button>
        <pre id="output"></pre>
      </main>
    </div>
  );
}
