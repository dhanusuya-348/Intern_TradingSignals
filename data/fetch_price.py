# data/fetch_price.py

import requests
import pandas as pd
from config import BINANCE_BASE_URL, HISTORICAL_LIMIT

def get_price_data(symbol: str, interval: str) -> pd.DataFrame:
    """
    Fetch historical OHLCV candlestick data for a given symbol and interval from Binance.
    Returns a cleaned DataFrame with datetime index.
    """
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": HISTORICAL_LIMIT
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error fetching data from Binance: {e}")
        return pd.DataFrame()

    # Convert response to DataFrame
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    # Clean up
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)

    return df
