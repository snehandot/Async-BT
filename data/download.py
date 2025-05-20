import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from binance.client import Client
import pandas as pd
from config.config import API_KEY, API_SECRET, SYMBOL

client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binance.vision/api'

def fetch_ohlcv(symbol, interval, limit=500):
    data = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(data, columns=[
        "timestamp", "Open", "High", "Low", "Close", "Volume",
        "close_time", "qav", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])
    df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("Date", inplace=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    return df

if __name__ == "__main__":
    df_15m = fetch_ohlcv(SYMBOL, "15m", 500)
    df_1h = fetch_ohlcv(SYMBOL, "1h", 500)

    df_15m.to_csv("data/15m.csv")
    df_1h.to_csv("data/1h.csv")

    print("✅ Saved data/15m.csv and data/1h.csv")