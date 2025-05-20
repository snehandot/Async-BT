import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

bt = pd.read_csv("data/backtest_trades.csv")
live = pd.read_csv("data/live_trades.csv")

merged = pd.merge_asof(bt.sort_values('ExitTime'),
                       live.sort_values('Timestamp'),
                       left_on='ExitTime', right_on='Timestamp',
                       direction='nearest')
print(merged)