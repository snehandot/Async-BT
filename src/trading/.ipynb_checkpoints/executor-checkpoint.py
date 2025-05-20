import threading
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config.config import SYMBOL, TRADE_QTY
from src.trading.exchange import fetch_ohlcv, place_test_order
from src.utils.logger import log_trade
from src.utils.plotter import run_live_chart


def live_trade_loop():
    while True:
        print("Market check now")
        df_15m = fetch_ohlcv(SYMBOL, "15m", 3)

        if df_15m.empty or len(df_15m) < 2:
            print("Not enough data to compare.")
            time.sleep(5)
            continue

        last = df_15m['Close'].iloc[-1]
        prev = df_15m['Close'].iloc[-2]

        print("Previous close:", prev, "Current close:", last)

        if last > prev:
            print("BUY signal")
            place_test_order(SYMBOL, "BUY", TRADE_QTY)
            log_trade("BUY", last)
        elif last < prev:
            print("SELL signal")
            place_test_order(SYMBOL, "SELL", TRADE_QTY)
            log_trade("SELL", last)
        else:
            print("No change — no trade")

        time.sleep(5)

if __name__ == "__main__":
    # Run trading loop in background thread
    trade_thread = threading.Thread(target=live_trade_loop, daemon=True)
    trade_thread.start()

    # Run live chart on main thread
    run_live_chart()