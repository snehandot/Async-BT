import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from runner import Backtest
import pandas as pd
from src.strategy.multi_tf import MultiTFStrategy


# data1 = pd.read_csv("15m.csv", index_col="Date", parse_dates=True)
# data2 = pd.read_csv("1h.csv", index_col="Date", parse_dates=True)

# portfolio_15m=[data1,data1,data1] # Give inputs of different asset to execute async buy-sell calls for all of them asynchronously.
# portfolio_1h=[data2,data2,data2] 
portfolio=["BTCUSDT", "ETHUSDT", "SOLUSDT", "BCHUSDT", "LTCUSDT"]

bt = Backtest(portfolio, MultiTFStrategy,1000, cash=100000000)
bt.execute_async()
# stats=bt.run()

# results['trades'].to_csv("data/backtest_trades.csv")
# bt.plot()