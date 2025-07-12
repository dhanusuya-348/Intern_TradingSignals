#strategies\rsi_volatility_strategy.py

from indicators.rsi import calculate_rsi
from indicators.volatility import calculate_volatility

def rsi_volatility_signal(df):
    if len(df) < 14:
        return {"strategy": "RSI+Volatility", "signal": "HOLD", "confidence": 50}

    try:
        rsi_val, rsi_signal = calculate_rsi(df)
        volatility = calculate_volatility(df)
        price = df["close"].iloc[-1]
    except Exception:
        return {"strategy": "RSI+Volatility", "signal": "HOLD", "confidence": 50}

    if rsi_signal == "oversold" and volatility == "low":
        signal, confidence = "BUY", 65
    elif rsi_signal == "overbought" and volatility == "high":
        signal, confidence = "SELL", 65
    else:
        signal, confidence = "HOLD", 50

    return {
        "strategy": "RSI+Volatility",
        "signal": signal,
        "confidence": confidence,
        "rsi_signal": rsi_signal,
        "volatility": volatility,
        "risk_reward_ratio": 1.8,
        "expected_profit_percent": 0.9,
        "stop_loss": price * 0.986,
        "take_profit": price * 1.012,
        "estimated_duration_minutes": 60
    }
