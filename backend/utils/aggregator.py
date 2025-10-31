# backend/utils/aggregator.py
import requests
import pandas as pd
import yfinance as yf

# Put your API keys here if you have them (optional)
TWELVEDATA_API_KEY = "0a034776b69f4c5f94d34378dadddcde"
FMP_API_KEY = "SFYenV3urEARrMlUxEQuzyYrlELekONc"


def fetch_yahoo(symbol: str, period="1mo", interval="1d"):
    """
    Fetch data via yfinance. Returns DataFrame with DateTime index and 'Close' column (and others).
    """
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, threads=False)
        if df is None or df.empty:
            return None
        # keep standard columns
        df = df.rename_axis('Datetime')
        # ensure index is datetime
        df.index = pd.to_datetime(df.index)
        df["Source"] = "Yahoo"
        return df  # has Open, High, Low, Close, Volume
    except Exception as e:
        print("Yahoo error:", e)
        return None


def fetch_twelvedata(symbol: str, interval="1day", outputsize=30):
    """
    Fetch data from TwelveData (if available). Returns DataFrame with datetime index and Close column.
    """
    try:
        if not TWELVEDATA_API_KEY:
            return None
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": TWELVEDATA_API_KEY
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if "values" not in data:
            # TwelveData often rejects .NS symbols; caller will catch this
            print("TwelveData error:", data)
            return None
        df = pd.DataFrame(data["values"])
        # Ensure datetime index
        # TwelveData returns 'datetime' column
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index("datetime")
        # rename cols to standard
        df = df.rename(columns={"close": "Close", "open": "Open", "high": "High", "low": "Low", "volume": "Volume"})
        # convert numeric
        df[["Close", "Open", "High", "Low", "Volume"]] = df[["Close", "Open", "High", "Low", "Volume"]].apply(pd.to_numeric, errors="coerce")
        df["Source"] = "TwelveData"
        return df
    except Exception as e:
        print("TwelveData error:", e)
        return None


def fetch_fmp(symbol: str):
    """
    Fetch data from FinancialModelingPrep (if available). Returns DataFrame with date index and Close col.
    """
    try:
        if not FMP_API_KEY:
            return None
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}"
        params = {"apikey": FMP_API_KEY}
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if not data or "historical" not in data:
            print("FMP error:", data)
            return None
        df = pd.DataFrame(data["historical"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        df = df.rename(columns={"close": "Close", "open": "Open", "high": "High", "low": "Low", "volume": "Volume"})
        df["Source"] = "FMP"
        # ensure numeric
        df[["Close", "Open", "High", "Low", "Volume"]] = df[["Close", "Open", "High", "Low", "Volume"]].apply(pd.to_numeric, errors="coerce")
        return df
    except Exception as e:
        print("FMP error:", e)
        return None


def normalize_index_to_naive(df: pd.DataFrame):
    """
    Convert any tz-aware index to tz-naive, ensure datetime index.
    """
    if df is None or df.empty:
        return df
    df.index = pd.to_datetime(df.index)
    # Attempt to remove tz if present
    try:
        # if index has tzinfo, tz_convert will work
        if getattr(df.index, "tz", None) is not None:
            try:
                df.index = df.index.tz_convert(None)
            except Exception:
                df.index = df.index.tz_localize(None)
    except Exception:
        # ignore if anything fails
        pass
    return df


def aggregate_stock_data(symbol: str):
    """
    Try multiple sources and return (combined_df, news_list).
    combined_df: DataFrame indexed by datetime with a 'Close' column (and others).
    news_list: list of strings (may be empty)
    """
    news_list = []
    frames = []

    # Try a set of symbol variants commonly used for Indian stocks
    variants = [symbol]
    if not symbol.endswith(".NS") and not symbol.endswith(".BO") and symbol.isalpha():
        variants += [f"{symbol}.NS", f"{symbol}.BO"]

    # Prefer Yahoo first (common, flexible)
    yahoo_df = None
    for sym in variants:
        yahoo_df = fetch_yahoo(sym)
        if yahoo_df is not None:
            print(f"✅ Yahoo returned data for {sym}")
            yahoo_df = normalize_index_to_naive(yahoo_df)
            frames.append(yahoo_df)
            break
        else:
            print(f"ℹ️ Yahoo no data for {sym}")

    # Try TwelveData (may fail for certain symbols / free-tier)
    td_df = fetch_twelvedata(symbol)
    if td_df is not None:
        print("✅ TwelveData returned data")
        td_df = normalize_index_to_naive(td_df)
        frames.append(td_df)
    else:
        print("ℹ️ TwelveData: no data / error")

    # Try FMP
    fmp_df = fetch_fmp(symbol)
    if fmp_df is not None:
        print("✅ FMP returned data")
        fmp_df = normalize_index_to_naive(fmp_df)
        frames.append(fmp_df)
    else:
        print("ℹ️ FMP: no data / error or legacy endpoint")

    # If no frames found, return None
    if not frames:
        print(f"❌ No valid data sources for {symbol}")
        return None, []

    # Normalize and keep only relevant columns; align by datetime index
    cleaned_frames = []
    for df in frames:
        # keep standard columns and ensure 'Close' exists
        if "Close" not in df.columns:
            # try lowercase
            if "close" in df.columns:
                df = df.rename(columns={"close": "Close"})
        # If df has numeric close values in a non-standard column, try to find it
        if "Close" not in df.columns:
            # skip if no Close
            continue
        # Reduce to standard columns if present
        cols = []
        for c in ["Open", "High", "Low", "Close", "Volume", "Source"]:
            if c in df.columns:
                cols.append(c)
        df_small = df[cols].copy()
        cleaned_frames.append(df_small)

    if not cleaned_frames:
        print("❌ After cleaning, no frames with 'Close' column")
        return None, []

    # Concatenate vertically, group by index (datetime) and average numeric cols
    combined = pd.concat(cleaned_frames)
    combined = combined.groupby(level=0).mean(numeric_only=True)  # average numeric columns
    # In addition, try to preserve a 'Source' column by listing sources per timestamp
    # But since we averaged numeric columns, we'll just keep combined numeric result.
    combined = combined.sort_index()
    combined = combined.dropna(subset=["Close"])

    # Deduplicate index and sort
    combined = combined[~combined.index.duplicated(keep='first')].sort_index()

    return combined, news_list
