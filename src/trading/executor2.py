import sys
import os
import threading
import time
import pandas as pd
import csv
from datetime import datetime
from collections import namedtuple

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config.config import SYMBOL, TRADE_QTY
from src.trading.exchange import fetch_ohlcv, place_test_order
from src.utils.plotter import run_live_chart

from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from ta.trend import SMAIndicator

equity = 100000  
risk_pct = 0.01  
max_trades = 10
cooldown_secs = 5

# State
trade_count = 0
last_trade_time = 0
position = "FLAT"  
entry_price = None
trade_log = []
Trade = namedtuple("Trade", ["timestamp", "action", "price", "size", "pnl"])

# Setup CSV
if not os.path.exists("data/live_trades.csv"):
    with open("data/live_trades.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Direction", "Entry Price", "Exit Price", "Size", "PnL", "Source"])

def log_live_trade(action, entry_price, exit_price=None, size=TRADE_QTY, pnl=None, meta="live_executor"):
    with open("data/live_trades.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(),
            action,
            entry_price,
            exit_price if exit_price else "",
            size,
            pnl if pnl else "",
            meta
        ])

def calculate_atr_position_size(atr_value):
    if pd.isna(atr_value) or atr_value == 0:
        return TRADE_QTY
    dollar_risk = equity * risk_pct
    size = dollar_risk / atr_value
    return round(min(max(size, 0.001), 5), 5)

def summarize_trades():
    df = pd.DataFrame(trade_log, columns=["timestamp", "action", "price", "size", "pnl"])
    print("\n🔚 Execution Complete. Trade Summary:")
    print(df)

    print(f"\n📊 Total trades: {len(df)}")
    print(f"BUYs: {len(df[df['action'] == 'BUY'])}, SELLs: {len(df[df['action'] == 'SELL'])}")
    print(f"Avg BUY price: {df[df['action'] == 'BUY']['price'].mean():.2f}" if not df[df['action'] == 'BUY'].empty else "No BUYs")
    print(f"Avg SELL price: {df[df['action'] == 'SELL']['price'].mean():.2f}" if not df[df['action'] == 'SELL'].empty else "No SELLs")
    if not df['pnl'].isna().all():
        print(f"Avg PnL: {df['pnl'].dropna().mean():.2f}")
        print(f"Total PnL: {df['pnl'].dropna().sum():.2f}")

def live_trade():
    global trade_count, last_trade_time, entry_price, equity, position

    while trade_count < max_trades:
        now = time.time()
        print(f"\n====== Market Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ======")

        df_15m = fetch_ohlcv(SYMBOL, "15m", 100)
        df_1h = fetch_ohlcv(SYMBOL, "1h", 100)

        if df_15m.empty or df_1h.empty or len(df_15m) < 20 or len(df_1h) < 20:
            print("⚠️ Insufficient data.")
            time.sleep(5)
            continue

        sma_1h = SMAIndicator(df_1h['Close'], window=20).sma_indicator().iloc[-1]
        rsi_1h = RSIIndicator(df_1h['Close'], window=14).rsi().iloc[-1]
        print("df_15m columns:", df_15m.columns.tolist())

        atr_15m = AverageTrueRange(df_15m['High'], df_15m['Low'], df_15m['Close'], window=14).average_true_range().iloc[-1]

        close_1h = df_1h['Close'].iloc[-1]
        close_15m = df_15m['Close'].iloc[-1]
        prev_15m = df_15m['Close'].iloc[-2]

        print(f"[1H] Close: {close_1h:.2f}, SMA: {sma_1h:.2f}, RSI: {rsi_1h:.2f}")
        print(f"[15M] Close: {close_15m:.2f}, Prev: {prev_15m:.2f}, ATR: {atr_15m:.4f}")

        # Risk confirmation
        confirm = close_1h > sma_1h and rsi_1h > 50

        if confirm and now - last_trade_time > cooldown_secs:
            size = calculate_atr_position_size(atr_15m)

            if close_15m > prev_15m and position != "LONG":
                print("→ BUY signal triggered")
                place_test_order(SYMBOL, "BUY", size)
                log_live_trade("BUY", close_15m, size=size)
                trade_log.append(Trade(datetime.now(), "BUY", close_15m, size, None))
                entry_price = close_15m
                position = "LONG"
                trade_count += 1
                last_trade_time = now

            elif close_15m < prev_15m and position != "SHORT":
                print("→ SELL signal triggered")
                pnl = None
                if position == "LONG" and entry_price:
                    pnl = (close_15m - entry_price) * size
                    equity += pnl
                    entry_price = None
                place_test_order(SYMBOL, "SELL", size)
                log_live_trade("SELL", close_15m, size=size, pnl=pnl)
                trade_log.append(Trade(datetime.now(), "SELL", close_15m, size, pnl))
                position = "SHORT"
                trade_count += 1
                last_trade_time = now
            else:
                print("→ Already in this position, no trade.")
        else:
            print("✗ No confirmation or cooldown active.")

        time.sleep(5)

    summarize_trades()

if __name__ == "__main__":
    trade_thread = threading.Thread(target=live_trade)
    trade_thread.start()
    run_live_chart()
