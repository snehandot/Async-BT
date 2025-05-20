import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from runner import Backtest
import pandas as pd
from src.strategy.multi_tf import MultiTFStrategy


data1 = pd.read_csv("15m.csv", index_col="Date", parse_dates=True)
data2 = pd.read_csv("1h.csv", index_col="Date", parse_dates=True)
bt = Backtest(data1,data2, MultiTFStrategy, cash=10000000000)
results = bt.execute()
stats=bt.run()

# results['trades'].to_csv("data/backtest_trades.csv")
bt.plot()