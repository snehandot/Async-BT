import sys
import os
import threading
import time
import pandas as pd
from datetime import datetime
from collections import namedtuple
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import time
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from src.trading.exchange import fetch_ohlcv
from config.config import SYMBOL

def live_append_plot():
    plt.ion()
    fig, ax = plt.subplots()
    plt.show(block=False)
    full_df = fetch_ohlcv(SYMBOL, "15m", 50)
    full_df.index = pd.to_datetime(full_df.index)

    while True:
        print("hi")
        new_df = fetch_ohlcv(SYMBOL, "15m", 2)
        new_df.index = pd.to_datetime(new_df.index)
        latest = new_df.iloc[-1:]

        if latest.index[-1] not in full_df.index:
            full_df = pd.concat([full_df, latest])

        ax.clear()
        mpf.plot(full_df, type='candle', ax=ax, style='charles', show_nontrading=True)
        plt.pause(1)

if __name__ == "__main__":
    live_append_plot()