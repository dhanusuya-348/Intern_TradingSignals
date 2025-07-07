# indicators/macd.py

import pandas as pd

def calculate_macd(df):
    if df is None or df.empty or "close" not in df.columns:
        return "neutral"

    close = df["close"]
    # Use EMA-50 and EMA-200 instead of 12 & 26
    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()
    macd_line = ema50 - ema200
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    # Get current and previous histogram values for trend analysis
    current_hist = histogram.iloc[-1]
    prev_hist = histogram.iloc[-2] if len(histogram) > 1 else current_hist

    # Noise filter: Ignore tiny fluctuations
    threshold = 0.3

    if current_hist > threshold and prev_hist <= threshold:
        return "bullish"
    elif current_hist < -threshold and prev_hist >= -threshold:
        return "bearish"
    elif current_hist > prev_hist and current_hist > threshold:
        return "bullish"
    elif current_hist < prev_hist and current_hist < -threshold:
        return "bearish"
    elif abs(current_hist) < threshold:
        return "neutral"
    else:
        return "bullish" if current_hist > 0 else "bearish"
