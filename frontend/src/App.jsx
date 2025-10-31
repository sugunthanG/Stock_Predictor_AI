import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [symbol, setSymbol] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    if (!symbol.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await axios.post("http://127.0.0.1:5000/predict", { symbol });
      setResult(res.data);
    } catch (err) {
      console.error("Axios error:", err);
      setError(err.response?.data?.error || "Failed to fetch prediction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>📊 SmartFin Stock Predictor AI</h1>

      <div className="input-section">
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="Enter Stock Symbol (e.g., TCS, INFY, RELIANCE)"
        />
        <button onClick={handlePredict} disabled={loading}>
          {loading ? "Analyzing..." : "Predict"}
        </button>
      </div>

      {error && <p className="error">⚠️ {error}</p>}

      {/* Display Results */}
      {result && !error && (
        <div className="result-box">
          <h2>📈 Stock Overview — {result.symbol}</h2>

          {/* Last 10 Days */}
          {result.last_10_days && (
            <>
              <h3>Last 10 Days (₹):</h3>
              <ul>
                {Object.entries(result.last_10_days).map(([date, price]) => (
                  <li key={date}>
                    {new Date(date).toLocaleDateString()} — ₹{price}
                  </li>
                ))}
              </ul>
            </>
          )}

          {/* Today Trend */}
          {result.today_trend && result.today_trend.length > 0 && (
            <>
              <h3>Today's Trend:</h3>
              <ul>
                {result.today_trend.map((item, idx) => (
                  <li key={idx}>
                    {new Date(item.time).toLocaleString()} — ₹{item.close}
                  </li>
                ))}
              </ul>
            </>
          )}

          {/* News Section */}
          {result.news && result.news.length > 0 && (
            <>
              <h3>📰 Latest News:</h3>
              <ul>
                {result.news.map((n, i) => (
                  <li key={i}>{n}</li>
                ))}
              </ul>
            </>
          )}

          <hr />

          {/* Prediction Results */}
          <h2>🤖 AI Prediction</h2>
          <p>
            Tomorrow’s Trend: <strong>{result.tomorrow_prediction}</strong>
          </p>
          <p>
            Suggestion: <strong>{result.suggestion}</strong>
          </p>

          {result.raw_prediction_value !== undefined && (
            <p>
              Probability of Rise:{" "}
              <strong>{(result.raw_prediction_value * 100).toFixed(2)}%</strong>
            </p>
          )}

          {/* Explanation Section */}
          {result.explanation && (
            <>
              <h3>Model Explanation:</h3>
              <ul>
                <li>
                  Latest Return:{" "}
                  {result.explanation.latest_return
                    ? result.explanation.latest_return.toFixed(4)
                    : "N/A"}
                </li>
                <li>
                  Probability (Up):{" "}
                  {result.explanation.probability_up
                    ? (result.explanation.probability_up * 100).toFixed(2) + "%"
                    : "N/A"}
                </li>
                <li>Model Type: {result.explanation.model_type}</li>
              </ul>
            </>
          )}

          {/* Feature Importance */}
          {result.feature_importance &&
            Object.keys(result.feature_importance).length > 0 && (
              <>
                <h3>Feature Importance:</h3>
                <ul>
                  {Object.entries(result.feature_importance).map(
                    ([feature, value]) => (
                      <li key={feature}>
                        {feature}:{" "}
                        {value !== null
                          ? value.toFixed(4)
                          : "Not calculated"}
                      </li>
                    )
                  )}
                </ul>
              </>
            )}
        </div>
      )}
    </div>
  );
}

export default App;
