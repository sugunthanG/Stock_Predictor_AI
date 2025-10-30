import { useState } from "react";
import axios from "axios";
import './App.css';

function App() {
  const [symbol, setSymbol] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    if (!symbol) return;
    setLoading(true);
    try {
      const res = await axios.post("http://127.0.0.1:5000/predict", { symbol });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setResult({ error: "Failed to fetch prediction" });
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 text-center">
      <h1 className="text-3xl font-bold mb-6 text-blue-600">Real Stock Predictor AI</h1>

      <input
        className="border p-2 rounded mb-4 w-60"
        placeholder="Enter Stock Symbol (e.g., TATA)"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
      />

      <button
        onClick={handlePredict}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        {loading ? "Predicting..." : "Predict"}
      </button>

      {result && !result.error && (
        <div className="mt-6 p-4 bg-white rounded shadow-md w-96 text-black text-left">
          <h2 className="text-xl font-semibold mb-2">{result.symbol}</h2>

          <h3 className="font-medium mt-2">Last 10 Days Prices:</h3>
          <ul className="list-disc ml-5">
            {Object.entries(result.last_10_days).map(([time, price]) => (
              <li key={time}>{time}: {price}</li>
            ))}
          </ul>

          <h3 className="font-medium mt-2">Latest News:</h3>
          <ul className="list-disc ml-5">
            {result.news.map((item, idx) => <li key={idx}>{item}</li>)}
          </ul>

          <h3 className="font-medium mt-2">Today Trend:</h3>
          <ul className="list-disc ml-5">
            {result.today_trend.map((item, idx) => (
              <li key={idx}>{item.time}: {item.close}</li>
            ))}
          </ul>

          <p className="text-lg font-bold mt-2">Tomorrow Prediction: {result.tomorrow_prediction}</p>
          <p className="mt-2 font-medium">AI Suggestion: {result.suggestion}</p>
        </div>
      )}

      {result && result.error && (
        <p className="text-red-500 mt-4">{result.error}</p>
      )}
    </div>
  );
}

export default App;
