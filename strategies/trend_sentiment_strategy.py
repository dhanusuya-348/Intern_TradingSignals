from indicators.trend import identify_trend

def trend_sentiment_signal(df, sentiment):
    trend = identify_trend(df)

    if trend == "uptrend" and sentiment == "bullish":
        signal, confidence = "BUY", 75
    elif trend == "downtrend" and sentiment == "bearish":
        signal, confidence = "SELL", 75
    else:
        signal, confidence = "HOLD", 50

    return {
        "strategy": "Trend+Sentiment",
        "signal": signal,
        "confidence": confidence,
        "sentiment": sentiment,
        "risk_reward_ratio": 2.2,
        "expected_profit_percent": 1.4,
        "stop_loss": df["close"].iloc[-1] * 0.985,
        "take_profit": df["close"].iloc[-1] * 1.015,
        "estimated_duration_minutes": 90
    }
