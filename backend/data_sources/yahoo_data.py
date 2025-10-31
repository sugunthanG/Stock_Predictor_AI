import yfinance as yf
import pandas as pd

def get_yahoo_data(symbol, period="1mo", interval="1h"):
    try:
        stock = yf.download(symbol, period=period, interval=interval)
        if stock.empty:
            return None
        stock.reset_index(inplace=True)
        stock.rename(columns={"Close": "Close"}, inplace=True)
        stock.set_index("Datetime" if "Datetime" in stock.columns else "Date", inplace=True)
        return stock[["Close"]]
    except Exception as e:
        print("Yahoo Finance exception:", e)
        return None
