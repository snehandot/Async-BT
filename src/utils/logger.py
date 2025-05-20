import csv
from datetime import datetime
import os

def log_trade(action, price):
    timestamp = datetime.now()
    try:
        import __main__
        script_name = os.path.basename(__main__.__file__)
    except Exception:
        pass

    with open("data/live_trades.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, action, price, script_name])