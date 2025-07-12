#strategies\bollinger_squeezer_strategy.py

from indicators.bollinger import calculate_bollinger_bands

def bollinger_squeeze_signal(df):
    if len(df) < 20:
        return {"strategy": "Bollinger Squeeze", "signal": "HOLD", "confidence": 50}

    try:
        bb_signal = calculate_bollinger_bands(df)
        price = df["close"].iloc[-1]
    except Exception:
        return {"strategy": "Bollinger Squeeze", "signal": "HOLD", "confidence": 50}

    if bb_signal == "breakout_up":
        signal, confidence = "BUY", 70
    elif bb_signal == "breakout_down":
        signal, confidence = "SELL", 70
    else:
        signal, confidence = "HOLD", 50

    return {
        "strategy": "Bollinger Squeeze",
        "signal": signal,
        "confidence": confidence,
        "bollinger": bb_signal,
        "risk_reward_ratio": 2.5,
        "expected_profit_percent": 1.6,
        "stop_loss": price * 0.982,
        "take_profit": price * 1.018,
        "estimated_duration_minutes": 75
    }
