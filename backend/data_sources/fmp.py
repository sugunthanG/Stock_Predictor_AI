import requests
import pandas as pd

API_KEY = "SFYenV3urEARrMlUxEQuzyYrlELekONc"  # Replace with your FMP API key

def get_fmp_data(symbol):
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/1hour/{symbol}?apikey={API_KEY}"
        res = requests.get(url)
        data = res.json()
        if not data or isinstance(data, dict) and data.get("Error Message"):
            print("FMP error:", data)
            return None

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.astype({
            "open": float, "high": float, "low": float, "close": float, "volume": float
        })
        df.set_index("date", inplace=True)
        df.rename(columns={"close": "Close"}, inplace=True)
        return df[["Close"]]
    except Exception as e:
        print("FMP exception:", e)
        return None

def get_news(symbol):
    # Placeholder: Replace with real news API if needed
    return [f"{symbol} news headline 1", f"{symbol} news headline 2"]
