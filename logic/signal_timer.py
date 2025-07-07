# signal_timer.py

def estimate_signal_duration(signal_type, confidence, trend, sentiment, volatility, timeframe):
    """
    Estimate signal duration intelligently based on real-time contextual inputs.

    Returns duration in minutes.
    """
    base_duration = {
        '1m': 15, '5m': 30, '15m': 60,
        '1h': 120, '4h': 240,
        '1d': 1440
    }.get(timeframe, 60)  # fallback = 60 mins

    multiplier = 1.0

    # Trend strength impact
    if trend == "uptrend" or trend == "downtrend":
        multiplier += 0.25
    elif trend == "sideways":
        multiplier -= 0.2

    # Sentiment impact
    if sentiment == "bullish" and signal_type == "BUY":
        multiplier += 0.15
    elif sentiment == "bearish" and signal_type == "SELL":
        multiplier += 0.15
    elif sentiment == "bullish" and signal_type == "SELL":
        multiplier -= 0.1
    elif sentiment == "bearish" and signal_type == "BUY":
        multiplier -= 0.1

    # Volatility impact
    if volatility == "low":
        multiplier += 0.1
    elif volatility == "high":
        multiplier -= 0.15

    # Confidence adjustment (stronger signals can run longer)
    if confidence >= 80:
        multiplier += 0.25
    elif confidence <= 55:
        multiplier -= 0.15

    # Clamp multiplier between 0.6x and 1.6x
    multiplier = max(0.6, min(multiplier, 1.6))

    final_duration = int(base_duration * multiplier)
    return final_duration
