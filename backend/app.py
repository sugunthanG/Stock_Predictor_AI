from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import requests

app = Flask(__name__)
CORS(app)  # Allow cross-origin for React

# Fetch last 20 days price data
def get_stock_data(symbol):
    stock = yf.download(symbol, period="1mo", interval="1h")
    if stock.empty:
        return None
    stock['Return'] = stock['Close'].pct_change()
    stock.dropna(inplace=True)
    return stock

# Predict next day trend
def predict_stock(stock):
    X = stock[['Return']]
    y = np.where(stock['Return'].shift(-1) > 0, 1, 0)
    X.dropna(inplace=True)
    y = y[-len(X):]  # align length
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = LogisticRegression(max_iter=500)
    model.fit(X_scaled, y)
    
    latest_return = np.array([[X['Return'].iloc[-1]]])
    latest_scaled = scaler.transform(latest_return)
    pred = model.predict(latest_scaled)[0]
    return "UP 📈" if pred == 1 else "DOWN 📉"

# Fetch news (optional, requires NewsAPI key)
def get_stock_news(symbol):
    API_KEY = "bb28616d58144571ab9745e56e9cc708"  # Replace with your key or leave empty
    if not API_KEY:
        return ["News API not configured."]
    url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&language=en&apiKey={API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        articles = data.get('articles', [])
        return [f"{a['title']} ({a['publishedAt'][:10]})" for a in articles[:10]]
    except:
        return ["Failed to fetch news."]

# Suggestion based on prediction
def get_suggestion(prediction):
    return "You can buy this stock ✅" if prediction == "UP 📈" else "Not recommended to buy ❌"

@app.route('/')
def home():
    return "✅ Flask backend is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        if not symbol:
            return jsonify({"error": "Please provide a stock symbol"}), 400

        stock = get_stock_data(symbol)
        if stock is None:
            return jsonify({"error": f"No data found for {symbol}"}), 404

        prediction = predict_stock(stock)
        news = get_stock_news(symbol)
        suggestion = get_suggestion(prediction)

        last_10_days = stock['Close'][-10:].round(2).to_dict()
        today_trend = [{"time": str(t), "close": c} for t, c in zip(stock.index[-8:], stock['Close'][-8:])]

        return jsonify({
            "symbol": symbol,
            "last_10_days": last_10_days,
            "news": news,
            "today_trend": today_trend,
            "tomorrow_prediction": prediction,
            "suggestion": suggestion
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
