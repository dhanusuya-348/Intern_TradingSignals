# backtesting/evaluator.py
#to print the backtest report in the terminal

from prettytable import PrettyTable
import pandas as pd

def evaluate_backtest_results(df):
    if "result" not in df.columns:
        print("\n⚠️ No 'result' column in backtest data. Skipping evaluation.")
        return {}

    total_signals = len(df)
    success_signals = df[df['result'] == 'SUCCESS']
    failed_signals = df[df['result'] == 'FAILURE']
    neutral_signals = df[df['result'] == 'NEUTRAL']

    buy_signals = df[df['signal'] == 'BUY']
    sell_signals = df[df['signal'] == 'SELL']
    hold_signals = df[df['signal'] == 'HOLD']

    success_rate = round((len(success_signals) / total_signals) * 100, 2) if total_signals else 0
    avg_profit = round(df['net_return_percent'].mean(), 2) if 'net_return_percent' in df.columns else 0.0

    # ✅ Cumulative Net Return (Compounded Growth)
    if "net_return_percent" in df.columns:
        df["return_multiplier"] = 1 + (df["net_return_percent"] / 100)
        cumulative_return = round((df["return_multiplier"].prod() - 1) * 100, 2)
    else:
        cumulative_return = 0.0

    # ✅ Total Gains and Losses
    total_gains = round(success_signals["net_return_percent"].sum(), 2) if not success_signals.empty else 0.0
    total_losses = round(failed_signals["net_return_percent"].sum(), 2) if not failed_signals.empty else 0.0

    summary = {
        "Total Signals": total_signals,
        "Success Rate": f"{success_rate}%",
        "Avg Profit % (per trade)": f"{avg_profit}%",
        "Cumulative Net Return %": f"{cumulative_return}%",
        "Total Gains from Wins": f"{total_gains}%",
        "Total Losses from Failures": f"{total_losses}%",
        "BUY Signals": len(buy_signals),
        "SELL Signals": len(sell_signals),
        "HOLD Signals": len(hold_signals),
        "Successful Signals": len(success_signals),
        "Failed Signals": len(failed_signals),
        "Neutral Signals (HOLD)": len(neutral_signals),
    }

    print("\n📊 Backtest Evaluation Report:\n" + "-"*40)
    for k, v in summary.items():
        print(f"{k}: {v}")
    print("-"*40)

    print_detailed_backtest_table(df)

    return summary

def print_detailed_backtest_table(df):
    df = df.sort_values(by="timestamp")
    table = PrettyTable()
    table.field_names = [
        "Time", "Coin", "Open", "Close", "Profit/Loss %", "RSI",
        "Volatility", "MACD", "Sentiment", "BB", "Signal", "Confidence", "Result",
        "Exit", "TP", "SL", "Exit Reason", "Duration (min)"
    ]

    for _, row in df.iterrows():
        def safe_val(val):
            try:
                return round(float(val), 2)
            except:
                return "-"

        table.add_row([
            row["timestamp"].strftime('%Y-%m-%d %H:%M:%S'),
            row.get("coin", "-"),
            safe_val(row.get("open", 0.0)),
            safe_val(row.get("close", 0.0)),
            f"{safe_val(row.get('net_return_percent', 0.0))}%",
            f"{safe_val(row.get('rsi', '-'))} ({row.get('rsi_signal', '-')})",
            row.get("volatility", "-"),
            row.get("macd", "-"),
            row.get("sentiment", "-"),
            row.get("bollinger", "-"),
            row.get("signal", "-"),
            safe_val(row.get("confidence", "-")),
            row.get("result", "-"),
            safe_val(row.get("exit_price", 0.0)),
            safe_val(row.get("take_profit", 0.0)),
            safe_val(row.get("stop_loss", 0.0)),
            row.get("exit_reason", "-"),
            row.get("estimated_duration_minutes", "-")
        ])

    print("\n🧾 Detailed Backtest Table:")
    print(table)
