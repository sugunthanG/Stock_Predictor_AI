import requests
import pandas as pd

API_KEY = "L8D8N6QXGIOC7MXS"  # Replace with your own

def get_data(symbol):
    try:
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "apikey": API_KEY
        }
        res = requests.get("https://www.alphavantage.co/query", params=params)
        data = res.json().get("Time Series (Daily)", {})
        if not data:
            return None

        df = pd.DataFrame(data).T.astype(float)
        df.index = pd.to_datetime(df.index)
        df.rename(columns={"4. close": "Close"}, inplace=True)
        return df[["Close"]]
    except Exception as e:
        print("AlphaVantage exception:", e)
        return None
