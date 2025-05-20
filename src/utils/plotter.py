import matplotlib.pyplot as plt
import matplotlib.animation as animation
from config.config import SYMBOL
from src.trading.exchange import fetch_ohlcv
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates

price_history = pd.DataFrame()

def animate(i):
    global price_history
    try:
        latest = fetch_ohlcv(SYMBOL, "15m", 2)  
        if latest.empty:
            return

        latest = latest[~latest.index.isin(price_history.index)] 
        price_history = pd.concat([price_history, latest])
        price_history = price_history[~price_history.index.duplicated(keep='last')]  

        ax.clear()
        ax.plot(price_history.index, price_history['Close'], label='Close Price', color='blue')

        if price_history['Close'].iloc[-1] > price_history['Close'].iloc[-2]:
            ax.axvline(price_history.index[-1], color='green', linestyle='--', label='Buy Signal')

        ax.set_title(f"{SYMBOL} - 15m Price (Live Accumulated)")
        ax.set_ylabel("Price")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

    except Exception as e:
        print("Plot error:", e)

def run_live_chart():
    global fig, ax
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, animate, interval=5000)  # every 10s
    plt.show()