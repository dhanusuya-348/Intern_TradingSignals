# indicators/rsi.py

import pandas as pd

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> tuple[float, str]:
    """
    Calculates RSI from closing prices.
    Returns: (RSI value, signal: 'overbought', 'oversold', or 'neutral')
    """
    if df is None or df.empty or "close" not in df.columns:
        return 50.0, "neutral"

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Use exponential moving average for more responsive RSI
    alpha = 1.0 / period
    avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    latest_rsi = rsi.iloc[-1]

    if pd.isna(latest_rsi):
        return 50.0, "neutral"

    # RSI levels for crypto markets
    if latest_rsi > 75:  
        return latest_rsi, "overbought"
    elif latest_rsi < 25:  
        return latest_rsi, "oversold"
    else:
        return latest_rsi, "neutral"