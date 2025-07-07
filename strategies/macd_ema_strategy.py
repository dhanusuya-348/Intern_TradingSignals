from indicators.macd import calculate_macd
from indicators.trend import calculate_ema

def macd_ema_signal(df):
    df = df.copy()

    if len(df) < 50:
        return {"strategy": "MACD+EMA", "signal": "HOLD", "confidence": 50}

    df = calculate_ema(df, periods=[50])

    if "ema_50" not in df.columns or df["ema_50"].isna().all():
        return {"strategy": "MACD+EMA", "signal": "HOLD", "confidence": 50}

    try:
        ema_50 = df["ema_50"].iloc[-1]
        price = df["close"].iloc[-1]
        macd_signal = calculate_macd(df)
    except Exception:
        return {"strategy": "MACD+EMA", "signal": "HOLD", "confidence": 50}

    if macd_signal == "bullish" and price > ema_50:
        signal, confidence = "BUY", 70
    elif macd_signal == "bearish" and price < ema_50:
        signal, confidence = "SELL", 70
    else:
        signal, confidence = "HOLD", 50

    return {
        "strategy": "MACD+EMA",
        "signal": signal,
        "confidence": confidence,
        "macd": macd_signal,
        "risk_reward_ratio": 2.0,
        "expected_profit_percent": 1.2,
        "stop_loss": price * 0.985,
        "take_profit": price * 1.015,
        "estimated_duration_minutes": 120
    }
