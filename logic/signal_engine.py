# logic/signal_engine.py

from strategies.macd_ema_strategy import macd_ema_signal
from strategies.rsi_volatility_strategy import rsi_volatility_signal
from strategies.trend_sentiment_strategy import trend_sentiment_signal
from strategies.bollinger_squeezer_strategy import bollinger_squeeze_signal

def evaluate_strategies(df, sentiment, symbol):
    """
    Evaluates all individual strategies on a given timeframe's data.
    Returns a list of strategy decisions with signal and confidence.
    """
    return [
        macd_ema_signal(df),
        rsi_volatility_signal(df),
        trend_sentiment_signal(df, sentiment),
        bollinger_squeeze_signal(df)
    ]

def generate_signal(price_data, sentiment, symbol, min_agreeing=1, confidence_threshold=55, debug=False):
    final_votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    confidences = []
    total_strategies = []

    for tf, df in price_data.items():
        if df is None or df.empty or len(df) < 20:
            continue
        strategies = evaluate_strategies(df, sentiment, symbol)
        total_strategies.extend(strategies)

        if debug:
            print(f"\n[DEBUG] {tf.upper()} Strategies:")
            for strat in strategies:
                print(f"  → {strat['strategy']}: {strat['signal']} ({strat['confidence']}%)")

    for strat in total_strategies:
        final_votes[strat["signal"]] += 1
        confidences.append(strat["confidence"])

    buy_votes = final_votes["BUY"]
    sell_votes = final_votes["SELL"]
    avg_confidence = int(sum(confidences) / len(confidences)) if confidences else 50

    if buy_votes >= min_agreeing and avg_confidence >= confidence_threshold and buy_votes > sell_votes:
        final_signal = "BUY"
    elif sell_votes >= min_agreeing and avg_confidence >= confidence_threshold and sell_votes > buy_votes:
        final_signal = "SELL"
    else:
        final_signal = "HOLD"

    if debug:
        agreeing_strats = [s for s in total_strategies if s["signal"] == final_signal]
        print("\n[DEBUG] Signal Voting Summary:")
        print(f"  BUY votes:  {buy_votes}")
        print(f"  SELL votes: {sell_votes}")
        print(f"  HOLD votes: {final_votes['HOLD']}")
        print(f"  Avg Confidence: {avg_confidence}%")
        print(f"\n[DEBUG] Strategies agreeing with final signal ({final_signal}):")
        for s in agreeing_strats:
            print(f"  ✅ {s['strategy']}: {s['confidence']}%")

    return final_signal, avg_confidence


def generate_live_signal(price_data, sentiment, symbol, debug=True):
    """
    Stricter version of signal generator for real-ti me usage.
    Requires more agreement and higher confidence.
    """
    return generate_signal(
        price_data=price_data,
        sentiment=sentiment,
        symbol=symbol,
        min_agreeing=2,
        confidence_threshold=57,  #65 for more stricter trades
        debug=debug
    )

def generate_backtest_signal(price_data, sentiment, symbol, debug=False):
    """
    Looser signal generator for backtesting.
    Allows more frequent trade signals to assess strategy behavior across wider conditions.
    
    - Uses relaxed thresholds (min_agreeing=1, confidence_threshold=55).
    - Should be used only inside backtest engine to simulate realistic signal entry points.

    Parameters:
    - price_data (dict): timeframe to DataFrame
    - sentiment (float): latest sentiment score at that point in time
    - symbol (str): trading pair
    - debug (bool): enable detailed signal voting logs for backtesting

    Returns:
    - (signal: str, confidence: int)
    """
    return generate_signal(
        price_data=price_data,
        sentiment=sentiment,
        symbol=symbol,
        min_agreeing=1,
        confidence_threshold=55,
        debug=debug
    )
