import sys
import os
import threading
import time
import pandas as pd
from datetime import datetime
from collections import namedtuple
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config.config import SYMBOL, TRADE_QTY
from src.trading.exchange import fetch_ohlcv
from src.utils.plotter import run_live_chart

last_trade_time = 0
cooldown_secs = 3  
Trade = namedtuple("Trade", ["timestamp", "action", "price"])
trade_log = []
entry_price = None
equity = 100000

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

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def summarize_trades():
    df = pd.DataFrame(trade_log)
    print("\n=== LIVE STRATEGY STATS ===")
    print(f"Total Trades: {len(df)}")
    if len(df) < 2:
        print("Not enough trades to evaluate.")
        return

    trades = []
    for i in range(0, len(df)-1):
        buy = df.iloc[i]
        sell = df.iloc[i+1]
        if buy.action == "BUY" and sell.action == "SELL":
            ret = (sell.price - buy.price) / buy.price * 100
            trades.append(ret)

    if trades:
        trades = pd.Series(trades)
        print(f"Win Rate [%]: {100 * (trades > 0).mean():.2f}")
        print(f"Best Trade [%]: {trades.max():.2f}")
        print(f"Worst Trade [%]: {trades.min():.2f}")
        print(f"Avg Trade [%]: {trades.mean():.2f}")
        print(f"Final Equity [$]: {equity:.2f}")
    else:
        print("No valid BUY/SELL pairs yet.")

def live_trade():
    global last_trade_time, entry_price, equity

    while len(trade_log) < 5:
        print(trade_log)

        now = time.time()
        print("\n====== Market Check: {} ======".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        df_15m = fetch_ohlcv(SYMBOL, "15m", 50)
        df_1h = fetch_ohlcv(SYMBOL, "1h", 50)

        if len(df_1h) < 21 or len(df_15m) < 3:
            print("Insufficient data")
            time.sleep(5)
            continue

        close_1h = df_1h['Close'].iloc[-1]
        sma_1h = df_1h['Close'].rolling(20).mean().iloc[-1]
        rsi_1h = calc_rsi(df_1h['Close']).iloc[-1]

        close_15m = df_15m['Close'].iloc[-1]
        prev_15m = df_15m['Close'].iloc[-2]
        timestamp_15m = df_15m.index[-1]

        print(f"[1H] Close: {close_1h:.2f}, SMA-20: {sma_1h:.2f}, RSI: {rsi_1h:.2f}")
        print(f"[15M] Time: {timestamp_15m}, Close: {close_15m:.2f}, Prev: {prev_15m:.2f}")

        confirm = close_1h > sma_1h and rsi_1h > 50
        price_up = close_15m > prev_15m
        price_down = close_15m < prev_15m

        if confirm:
            print("✓ Confirmation met: Price above SMA and RSI > 50")
            if now - last_trade_time > cooldown_secs:
                if price_up:
                    print("→ Advanced BUY Signal")
                    log_live_trade("BUY", close_15m)
                    trade_log.append(Trade(datetime.now(), "BUY", close_15m))
                    entry_price = close_15m
                    last_trade_time = now
                elif price_down:
                    print("→ Advanced SELL Signal")
                    if entry_price:
                        pnl = (close_15m - entry_price) * TRADE_QTY
                        log_live_trade("SELL", entry_price, close_15m, TRADE_QTY, pnl)
                        trade_log.append(Trade(datetime.now(), "SELL", close_15m))
                        equity += pnl
                        entry_price = None
                    else:
                        log_live_trade("SELL", close_15m)
                        trade_log.append(Trade(datetime.now(), "SELL", close_15m))
                    last_trade_time = now
                else:
                    print("→ No significant 15m price movement — no trade")
            else:
                print("⏳ In cooldown period, skipping trade")
        else:
            print("✗ Confirmation failed: SMA or RSI condition not met")

        time.sleep(5)

    print("\n🔚 Trade limit reached. Summarizing results.")
    summarize_trades()

if __name__ == "__main__":
    trade_thread = threading.Thread(target=live_trade)
    trade_thread.start()
    run_live_chart()
