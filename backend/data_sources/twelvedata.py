import requests
import pandas as pd

API_KEY = "0a034776b69f4c5f94d34378dadddcde"  # Replace with your own

def get_twelvedata(symbol, interval="1day", outputsize=30):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "values" not in data:
        print("TwelveData error:", data.get("message", "Unknown"))
        return None

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.astype({
        "open": float, "high": float, "low": float, "close": float, "volume": float
    })
    df.set_index("datetime", inplace=True)
    df.rename(columns={"close": "Close"}, inplace=True)
    return df[["Close"]]
