#logic\risk_manager.py

import numpy as np
from fractions import Fraction

def calculate_atr(df, period=14):
    df = df.copy()
    df["H-L"] = df["high"] - df["low"]
    df["H-PC"] = abs(df["high"] - df["close"].shift(1))
    df["L-PC"] = abs(df["low"] - df["close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
    atr = df["TR"].rolling(window=period).mean()
    return round(atr.iloc[-1], 4) if not atr.empty else 0.0

def estimate_reward_multiplier(trend_strength, sentiment_score, volatility_level, confidence):
    multiplier = 1.8

    if trend_strength > 0.8:
        multiplier += 0.5
    elif trend_strength > 0.6:
        multiplier += 0.3
    elif trend_strength < 0.4:
        multiplier -= 0.3

    if sentiment_score > 0.6:
        multiplier += 0.2
    elif sentiment_score < -0.6:
        multiplier -= 0.2

    if volatility_level == "high":
        multiplier -= 0.25
    elif volatility_level == "low":
        multiplier += 0.1

    if confidence >= 85:
        multiplier += 0.35
    elif confidence <= 55:
        multiplier -= 0.35

    return round(np.clip(multiplier, 1.4, 4.0), 2)

def determine_risk_level(multiplier):
    if multiplier < 1.8:
        return "low"
    elif multiplier < 2.5:
        return "moderate"
    return "high"

def calculate_risk_management(df, signal, volatility_level, indicators, backtest_df=None, confidence=70):
    if df.empty or signal not in ["BUY", "SELL"]:
        return {
            'risk_reward_ratio': 0.0,
            'risk_reward_label': "1:0",
            'suggested_stop_loss': 0.0,
            'suggested_take_profit': 0.0,
            'risk_level': 'neutral',
            'expected_profit_percent': 0.0
        }

    entry_price = df["close"].iloc[-1]
    atr = calculate_atr(df)

    if atr == 0.0 or np.isnan(atr):
        return {
            'risk_reward_ratio': 0.0,
            'risk_reward_label': "1:0",
            'suggested_stop_loss': 0.0,
            'suggested_take_profit': 0.0,
            'risk_level': 'invalid',
            'expected_profit_percent': 0.0
        }

    sentiment = indicators.get("sentiment", 0.0)
    trend_strength = indicators.get("trend_strength", 0.5)
    volatility = indicators.get("volatility", "medium")

    reward_multiplier = estimate_reward_multiplier(trend_strength, sentiment, volatility, confidence)
    risk_level = determine_risk_level(reward_multiplier)

    # 🛡 Adaptive SL logic based on confidence
    if confidence >= 85:
        sl_multiplier = 1.2
    elif confidence <= 55:
        sl_multiplier = 0.8
    else:
        sl_multiplier = 1.0

    max_sl_percent = 1.5  # 💣 Don't allow SL > 1.5% from entry

    if signal == "BUY":
        raw_sl = atr * sl_multiplier
        stop_loss = round(entry_price - min(raw_sl, entry_price * max_sl_percent / 100), 4)
        take_profit = round(entry_price + (atr * reward_multiplier), 4)
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        raw_return = ((take_profit - entry_price) / entry_price) * 100
    else:
        raw_sl = atr * sl_multiplier
        stop_loss = round(entry_price + min(raw_sl, entry_price * max_sl_percent / 100), 4)
        take_profit = round(entry_price - (atr * reward_multiplier), 4)
        risk = stop_loss - entry_price
        reward = entry_price - take_profit
        raw_return = ((entry_price - take_profit) / entry_price) * 100

    risk_reward_ratio = round(reward / risk, 2) if risk != 0 else 0.0
    expected_profit_percent = round(abs(raw_return), 2)

    # ✅ Simplify as proper fraction using fractions module
    try:
        ratio = Fraction(risk).limit_denominator(1000) / Fraction(reward).limit_denominator(1000)
        simplified = ratio.limit_denominator()
        risk_reward_label = f"{simplified.numerator} : {simplified.denominator}"
    except:
        risk_reward_label = f"{round(risk, 2)} : {round(reward, 2)}"

    # ❌ Filter weak trades more strictly
    if risk_reward_ratio < 1.2 or expected_profit_percent < 0.25:
        return {
            'risk_reward_ratio': risk_reward_ratio,
            'risk_reward_label': risk_reward_label,
            'suggested_stop_loss': stop_loss,
            'suggested_take_profit': take_profit,
            'risk_level': 'too_weak',
            'expected_profit_percent': expected_profit_percent
        }

    return {
        'risk_reward_ratio': risk_reward_ratio,
        'risk_reward_label': risk_reward_label,
        'suggested_stop_loss': stop_loss,
        'suggested_take_profit': take_profit,
        'risk_level': risk_level,
        'expected_profit_percent': expected_profit_percent
    }