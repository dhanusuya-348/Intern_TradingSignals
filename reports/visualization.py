# reports/visualization.py

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_price_with_indicators(df, backtest_df, symbol, save_path):
    if not isinstance(backtest_df, pd.DataFrame):
        raise ValueError(f"Expected backtest_df to be a DataFrame, but got {type(backtest_df)}")

    # Generate base filename without extension
    base_path = save_path.rsplit('.', 1)[0] if '.' in save_path else save_path
    
    # Chart 1: Price chart with entry/exit points
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.plot(df['close'], label='Close Price', color='black', linewidth=1.5)
    avg_price = df['close'].mean()
    ax.axhline(avg_price, color='orange', linestyle='--', label='Avg Price', alpha=0.7)
    ax.text(df.index[-1], avg_price * 0.998, f' ${avg_price:.2f}', 
             verticalalignment='top', fontsize=10, color='orange', fontweight='bold')

    added_labels = set()

    if not backtest_df.empty and 'timestamp' in backtest_df.columns:
        backtest_df['timestamp'] = pd.to_datetime(backtest_df['timestamp'])
        df.index = pd.to_datetime(df.index)

        for i, (_, row) in enumerate(backtest_df.iterrows()):
            try:
                entry_time = pd.to_datetime(row['timestamp'])
                if entry_time in df.index:
                    entry_price = df.loc[entry_time, 'close']
                    signal = row.get('signal', 'HOLD')
                    result = row.get('result', 'NEUTRAL')
                    
                    # Set colors based on result
                    line_color = 'green' if result == 'SUCCESS' else 'red' if result == 'FAILURE' else 'gray'
                    marker_color = 'darkgreen' if result == 'SUCCESS' else 'darkred' if result == 'FAILURE' else 'gray'
                    marker = '^' if signal == 'BUY' else 'v' if signal == 'SELL' else 'o'
                    label = f"{signal} Entry ({result})"

                    display_label = label if label not in added_labels else None
                    added_labels.add(label)

                    # Plot entry point
                    ax.scatter(entry_time, entry_price, marker=marker, color=marker_color, 
                               s=120, zorder=5, label=display_label, edgecolors='white', linewidth=2)

                    # Plot entry-exit line without annotations
                    if 'exit_price' in row and not pd.isna(row['exit_price']):
                        exit_price = float(str(row['exit_price']).replace(',', ''))
                        exit_time = entry_time + pd.Timedelta(hours=1)
                        
                        ax.plot([entry_time, exit_time], [entry_price, exit_price], 
                                color=line_color, linewidth=3, alpha=0.8, zorder=4)
                        ax.scatter(exit_time, exit_price, marker='s', color=line_color, 
                                   s=80, zorder=5, alpha=0.8, edgecolors='white', linewidth=1)

            except Exception as e:
                print(f"[Warning] Could not plot backtest entry: {e}")

    ax.set_title(f"{symbol.upper()} - Price with Entry/Exit Points", fontweight='bold', fontsize=16)
    ax.set_ylabel("Price")
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    price_path = f"{base_path}_price.png"
    plt.savefig(price_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📈 Price chart saved to: {price_path}")

    # Chart 2: Individual Trade P&L bars
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    if not backtest_df.empty:
        trade_data = []
        for i, (_, row) in enumerate(backtest_df.iterrows()):
            if 'net_return_percent' in row and not pd.isna(row['net_return_percent']):
                trade_data.append({
                    'trade_num': i+1,
                    'pnl': row['net_return_percent'],
                    'result': row.get('result', 'NEUTRAL'),
                    'signal': row.get('signal', 'HOLD')
                })
        
        if trade_data:
            trade_df = pd.DataFrame(trade_data)
            colors = ['green' if r == 'SUCCESS' else 'red' if r == 'FAILURE' else 'gray' 
                     for r in trade_df['result']]
            
            bars = ax.bar(trade_df['trade_num'], trade_df['pnl'], color=colors, alpha=0.7, edgecolor='black')
            ax.axhline(0, color='black', linestyle='-', alpha=0.5)
            
            # Add value labels on bars
            for bar, pnl in zip(bars, trade_df['pnl']):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + (0.1 if height >= 0 else -0.1),
                        f'{pnl:.1f}%', ha='center', va='bottom' if height >= 0 else 'top', 
                        fontsize=10, fontweight='bold')

    ax.set_title(f"{symbol.upper()} - Individual Trade P&L", fontweight='bold', fontsize=16)
    ax.set_xlabel("Trade Number")
    ax.set_ylabel("Return %")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    pnl_path = f"{base_path}_pnl.png"
    plt.savefig(pnl_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 P&L chart saved to: {pnl_path}")

    # Chart 3: Cumulative returns
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    if not backtest_df.empty and 'net_return_percent' in backtest_df.columns:
        cumulative_returns = backtest_df['net_return_percent'].cumsum()
        
        ax.fill_between(range(len(cumulative_returns)), cumulative_returns, 
                        alpha=0.6, color='lightblue', label='Cumulative Returns')
        ax.plot(range(len(cumulative_returns)), cumulative_returns, color='blue', linewidth=2)
        ax.axhline(0, color='black', linestyle='-', alpha=0.3)
        
        # Add final cumulative return value
        final_return = cumulative_returns.iloc[-1] if len(cumulative_returns) > 0 else 0
        ax.text(len(cumulative_returns)-1, final_return, f' {final_return:.1f}%', 
                fontsize=12, fontweight='bold', color='blue')

    ax.set_title(f"{symbol.upper()} - Cumulative Returns", fontweight='bold', fontsize=16)
    ax.set_xlabel("Trade Sequence")
    ax.set_ylabel("Cumulative Return %")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    cumulative_path = f"{base_path}_cumulative.png"
    plt.savefig(cumulative_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📈 Cumulative returns chart saved to: {cumulative_path}")

    # Chart 4: Trade summary statistics
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    if not backtest_df.empty and 'result' in backtest_df.columns:
        summary = backtest_df['result'].value_counts()
        colors = ['green' if label == 'SUCCESS' else 'red' if label == 'FAILURE' else 'gray' 
                 for label in summary.index]
        
        wedges, texts, autotexts = ax.pie(summary, labels=summary.index, colors=colors, 
                                          autopct='%1.1f%%', startangle=140)
        
        # Add count annotations
        for i, (label, count) in enumerate(summary.items()):
            texts[i].set_text(f'{label}\n({count} trades)')
            texts[i].set_fontsize(12)
            autotexts[i].set_fontweight('bold')
            autotexts[i].set_fontsize(11)

    ax.set_title(f"{symbol.upper()} - Trade Results Distribution", fontweight='bold', fontsize=16)
    
    plt.tight_layout()
    summary_path = f"{base_path}_summary.png"
    plt.savefig(summary_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 Summary chart saved to: {summary_path}")

    print(f"🎯 All 4 charts saved as separate files with prefix: {base_path}")

def plot_backtest_results(df, save_path):
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected DataFrame for backtest results, got {type(df)}")

    if df.empty or 'result' not in df.columns:
        print("⚠️ No backtest data available for plotting.")
        return

    summary = df['result'].value_counts()
    colors = ['green' if label == 'SUCCESS' else 'red' if label == 'FAILURE' else 'gray' for label in summary.index]

    plt.figure(figsize=(6, 6))
    plt.pie(summary, labels=summary.index, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title("Backtest Result Distribution")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"📊 Backtest pie chart saved to: {save_path}")