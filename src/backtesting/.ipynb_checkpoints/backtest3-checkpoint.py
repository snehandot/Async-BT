import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backtesting import Backtest
import pandas as pd
from src.strategy.multi_tf import MultiTFStrategy

# Load 15m data
data_15m = pd.read_csv("data/15m.csv", index_col="Date", parse_dates=True)

bt = Backtest(data_15m, MultiTFStrategy, cash=100000000)
results = bt.run()
results['_trades'].to_csv("data/backtest_trades.csv", mode='a', header=not os.path.exists("data/backtest_trades.csv"))
print(results)



bt.plot()