# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from model.explain_model import train_and_predict
from utils.aggregator import aggregate_stock_data
import traceback

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return jsonify({"message": "✅ SMARTFIN Backend Running Successfully!"})


@app.route('/predict', methods=['POST'])
def predict():
    print("🔹 /predict route hit")

    try:
        data = request.get_json()
        print("📩 Received data:", data)

        if not data or "symbol" not in data:
            return jsonify({"error": "Please provide a valid stock symbol"}), 400

        symbol = data["symbol"].strip().upper()

        # Aggregate data
        print(f"📊 Aggregating data for symbol: {symbol}")
        stock_df, news_data = aggregate_stock_data(symbol)

        if stock_df is None or stock_df.empty:
            print(f"⚠️ No stock data found for {symbol}")
            return jsonify({"error": f"No valid data found for {symbol}"}), 404

        # Run model
        print(f"🧠 Running model for {symbol}")
        prediction_result = train_and_predict(stock_df)

        if not prediction_result or "prediction" not in prediction_result:
            print("⚠️ Prediction result missing expected fields")
            return jsonify({"error": "Model failed to generate prediction"}), 500

        print("✅ Prediction result generated successfully:", prediction_result)

        # Build response
        # Ensure index is JSON-serializable (string)
        last_10 = stock_df["Close"].tail(10).round(2)
        last_10_dict = {str(idx): float(val) for idx, val in last_10.items()}

        today_trend_idx = stock_df.index[-8:]
        today_trend_vals = stock_df["Close"].tail(8).astype(float).tolist()
        today_trend = [{"time": str(t), "close": float(c)} for t, c in zip(today_trend_idx, today_trend_vals)]

        response = {
            "symbol": symbol,
            "last_10_days": last_10_dict,
            "today_trend": today_trend,
            "tomorrow_prediction": prediction_result.get("prediction", "N/A"),
            "explanation": prediction_result.get("explanation", {}),
            "suggestion": prediction_result.get("suggestion", "N/A"),
            "news": news_data if news_data else [],
            "feature_importance": prediction_result.get("feature_importance", {}),
            "raw_prediction_value": prediction_result.get("raw_prediction_value")
        }

        return jsonify(response), 200

    except Exception as e:
        print("❌ Error in /predict route:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Starting SMARTFIN Flask backend on http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
