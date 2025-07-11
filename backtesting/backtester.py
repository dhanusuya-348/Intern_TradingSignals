# backtesting/backtester.py

import pandas as pd
from datetime import timedelta
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
from indicators.bollinger import calculate_bollinger_bands
from indicators.volatility import calculate_volatility
from logic.risk_manager import calculate_risk_management
from logic.signal_timer import estimate_signal_duration
#from logic.signal_engine import generate_backtest_signal
from logic.signal_engine import generate_live_signal as generate_backtest_signal

# Load historical sentiment data
url = "https://intern-tradingsignals.onrender.com/sentiment/csv"
sentiment_df = pd.read_csv(url, names=["timestamp", "symbol", "sentiment"], header=None)
sentiment_df["timestamp"] = pd.to_datetime(sentiment_df["timestamp"])

def sentiment_label_to_score(label):
    mapping = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}
    return mapping.get(label.lower().strip(), 0.0)

def get_historical_sentiment(symbol, ts):
    ts_rounded = ts.replace(minute=(ts.minute // 30) * 30, second=0, microsecond=0)
    filtered = sentiment_df[
        (sentiment_df["symbol"] == symbol) & 
        (sentiment_df["timestamp"] <= ts_rounded)
    ]
    if not filtered.empty:
        label = filtered.sort_values("timestamp").iloc[-1]["sentiment"]
        return sentiment_label_to_score(label)
    return 0.0

def run_backtest(price_df, symbol, interval, headlines, price_data_dict):
    backtest_results = []
    commission_rate = 0.002  # 0.2%
    next_trade_possible_at = price_df.index[0]

    for i in range(20, len(price_df) - 5):
        current_time = pd.to_datetime(price_df.index[i])
        if current_time < next_trade_possible_at:
            continue

        subset = price_df.iloc[:i]
        current = price_df.iloc[i]
        next_candles = price_df.iloc[i+1:i+6]
        sentiment_score = get_historical_sentiment(symbol, current_time)

        current_tf_data = {
            tf: df[df.index <= current_time].copy()
            for tf, df in price_data_dict.items()
        }

        signal, confidence = generate_backtest_signal(current_tf_data, sentiment_score, symbol)
        if signal == "HOLD":
            continue

        entry_price = current["close"]
        rsi_val, rsi_signal = calculate_rsi(subset)
        macd_signal = calculate_macd(subset)
        bb_signal = calculate_bollinger_bands(subset)
        volatility = calculate_volatility(subset)

        indicators = {
            "rsi": float(rsi_val),
            "macd": macd_signal,
            "bb": bb_signal,
            "volatility": volatility,
            "sentiment": sentiment_score,
            "trend_strength": 0.6
        }

        risk_info = calculate_risk_management(subset, signal, volatility, indicators, pd.DataFrame(backtest_results), confidence)
        stop_loss = risk_info["suggested_stop_loss"]
        take_profit = risk_info["suggested_take_profit"]

        estimated_duration_minutes = estimate_signal_duration(
            signal_type=signal,
            confidence=confidence,
            trend="uptrend" if macd_signal == "bullish" else "downtrend" if macd_signal == "bearish" else "sideways",
            sentiment="bullish" if sentiment_score > 0.3 else "bearish" if sentiment_score < -0.3 else "neutral",
            volatility=volatility,
            timeframe=interval
        )

        start_time = current_time
        end_time = current_time + timedelta(minutes=estimated_duration_minutes)
        next_trade_possible_at = end_time

        exit_price = None
        exit_reason = "TIME"
        for _, row in next_candles.iterrows():
            high, low = row["high"], row["low"]
            if signal == "BUY":
                if low <= stop_loss:
                    exit_price = stop_loss
                    exit_reason = "SL"
                    break
                elif high >= take_profit:
                    exit_price = take_profit
                    exit_reason = "TP"
                    break
            elif signal == "SELL":
                if high >= stop_loss:
                    exit_price = stop_loss
                    exit_reason = "SL"
                    break
                elif low <= take_profit:
                    exit_price = take_profit
                    exit_reason = "TP"
                    break

        if exit_price is None:
            exit_price = next_candles.iloc[-1]["close"]

        raw_return = (
            (exit_price - current["open"]) / current["open"] * 100 if signal == "BUY"
            else (current["open"] - exit_price) / current["open"] * 100
        )

        # ✅ FIXED: Correct result logic for TIME exits
        if exit_reason == "TP":
            result = "SUCCESS"
        elif exit_reason == "SL":
            result = "FAILURE"
        else:  # exit_reason == "TIME"
            # For TIME exits, check if the price moved in the expected direction
            if signal == "BUY":
                result = "SUCCESS" if exit_price > current["open"] else "FAILURE"
            else:  # signal == "SELL"
                result = "SUCCESS" if exit_price < current["open"] else "FAILURE"

        net_return = round(raw_return - (commission_rate * 100), 2)

        if abs(raw_return) < 0.25:
            print(f"⚠️ Weak signal at {current_time}: {signal} had only {raw_return:.2f}% return")

        backtest_results.append({
            "timestamp": current_time,
            "coin": symbol,
            "interval": interval,
            "open": current["open"],
            "close": current["close"],
            "exit_price": exit_price,
            "rsi": round(rsi_val, 2),
            "rsi_signal": rsi_signal,
            "macd": macd_signal,
            "bollinger": bb_signal,
            "sentiment": sentiment_score,
            "volatility": volatility,
            "signal": signal,
            "confidence": confidence,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "estimated_duration_minutes": estimated_duration_minutes,
            "risk_reward_ratio": risk_info["risk_reward_label"],
            "expected_profit_percent": risk_info["expected_profit_percent"],
            "risk_level": risk_info["risk_level"],
            "exit_reason": exit_reason,
            "net_return_percent": net_return,
            "result": result
        })

    df = pd.DataFrame(backtest_results)
    if not df.empty and "timestamp" in df.columns:
        df["Time"] = pd.to_datetime(df["timestamp"])
    else:
        print("⚠️ Warning: No valid backtest results generated.")
    return df
