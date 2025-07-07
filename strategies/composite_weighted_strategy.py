from indicators.macd import calculate_macd
from indicators.rsi import calculate_rsi
from indicators.bollinger import calculate_bollinger_bands
from indicators.volatility import calculate_volatility

def composite_weighted_signal(df, sentiment):
    score = 0

    macd = calculate_macd(df)
    if macd == "bullish":
        score += 3
    elif macd == "bearish":
        score -= 3

    rsi_val, rsi_state = calculate_rsi(df) if isinstance(calculate_rsi(df), tuple) else (None, calculate_rsi(df))

    if rsi_state == "oversold":
        score += 2
        if rsi_val and rsi_val < 25:
            score += 1
    elif rsi_state == "overbought":
        score -= 2
        if rsi_val and rsi_val > 75:
            score -= 1
    elif rsi_state == "neutral" and rsi_val:
        if 45 <= rsi_val <= 55:
            score += 1 if macd == "bullish" else -1

    if sentiment == "bullish":
        score += 2
    elif sentiment == "bearish":
        score -= 2

    bb = calculate_bollinger_bands(df)
    if bb == "breakout_up":
        score += 3
        if macd == "bullish":
            score += 1
    elif bb == "breakout_down":
        score -= 3
        if macd == "bearish":
            score -= 1
    elif bb == "within_range":
        score += 1 if rsi_state == "oversold" else -1 if rsi_state == "overbought" else 0

    volatility = calculate_volatility(df)
    if volatility == "low" and abs(score) >= 3:
        score += 1
    elif volatility == "high" and abs(score) < 3:
        score = int(score * 0.7)

    if score >= 6:
        return "BUY", min(95, 75 + score * 2)
    elif score <= -6:
        return "SELL", min(95, 75 + abs(score) * 2)
    elif score >= 3:
        return "BUY", min(85, 65 + score * 2)
    elif score <= -3:
        return "SELL", min(85, 65 + abs(score) * 2)
    else:
        return "HOLD", 50 + score * 2
