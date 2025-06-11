import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


# from backtesting import Strategy
from src.strategy.Strategy import Strategy
import pandas as pd
import numpy as np

class MultiTFStrategy(Strategy):
    def __init__(self,tick,session):
        super().__init__(tick,session)      # Init A
        self.tick=tick
        self.last_trade_idx = 1
        self.trades = []
        self.size=1

        # self.pos=1
        # self.rsi_1h = calc_rsi(df_1h['Close']).iloc[-1]

    def calc_rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))


    def next(self,nos):
        # self.buy(size=1)

        val=self.data
        idx = len(val)
        # print(idx)

        if idx - self.last_trade_idx < 10:
            return

        current_time = val.Close.index[-1].floor('H')
        if current_time not in self.data_1h.index:
            print("Bye")
            return

        close_1h = self.data_1h.loc[current_time, 'Close']
        sma_1h = self.data_1h['Close'].rolling(20).mean().loc[current_time]
        rsi_1h = self.calc_rsi(self.data_1h['Close']).loc[current_time]

        # if not np.isfinite(sma_1h) or not np.isfinite(rsi_1h):
        #     return

        confirm = True#close_1h > sma_1h and rsi_1h > 50
        price_up = val.Close[-1] > val.Close[-2]
        price_down = val.Close[-1] < val.Close[-2]

        # print(f"\nTime: {self.data.index[-1]}")
        # print(f"1H Close: {close_1h:.2f}, SMA-20: {sma_1h:.2f}, RSI: {rsi_1h:.2f}")
        # print(f"15m Close: {self.data.Close[-2]:.2f} → {self.data.Close[-1]:.2f}")
        # print(f"Confirm: {confirm}, Up: {price_up}, Down: {price_down}")

        if confirm:
            if price_up:
                self.buy(size=0.01)
                self.last_trade_idx = idx
                self.trades.append({'time':val.Close.index[-1],'action':'BUY','price':val.Close[-1],'size':0.001})
                print(f"✓ BUY executed from STRAT:{self.tick}")
            elif price_down:
                self.sell(size=0.01)
                self.last_trade_idx = idx
                self.trades.append({'time':val.Close.index[-1],'action':'SELL','price':val.Close[-1],'size':0.001})
                print(f"✓ SELL executed from STRAT{self.tick}")
        else:
            print(f"Not entering market from STRAT{tick}")


            
    async def next2(self, nos=1):
        # print(self.tick,self.size)
        # await self.buy(size=self.size)
        val = await self.data_1s             # 1s candles (live)
        val_1m = await self.data_1m          # 1m candles (live)
        # print("222")
    
        # if len(val_1m) < 20 or len(val) < 2:
        #     return
    
        latest_1m_time = val_1m.index[-1]
    
        try:
            close_1m = val_1m.loc[latest_1m_time, 'Close']
            sma_1m = val_1m['Close'].rolling(20).mean().loc[latest_1m_time]
            rsi_1m = self.calc_rsi(val_1m['Close']).loc[latest_1m_time]
        except KeyError:
            print("Key Error")
            return
    
        if pd.isna(sma_1m) or pd.isna(rsi_1m):
            print("No Data")
            return
    
        price_up = val['Close'].iloc[-1] > val['Close'].iloc[-2]
        price_down = val['Close'].iloc[-1] < val['Close'].iloc[-2]
        print(self.tick,rsi_1m,val['Close'].iloc[-1],price_up,price_down)
        if close_1m > sma_1m and rsi_1m > 40 and price_up:
            print(self.tick)
            await self.buy(size=self.size)
            self.trades.append({'time': val.Close.index[-1], 'action': 'BUY', 'price': val.Close[-1], 'size': 1})
            print(f"✓ BUY executed from STRAT: {self.tick}")
    
        elif close_1m < sma_1m and rsi_1m < 60 and price_down:
            await self.sell(size=self.size)
            self.trades.append({'time': val.Close.index[-1], 'action': 'SELL', 'price': val.Close[-1], 'size': 1})
            print(f"✓ SELL executed from STRAT: {self.tick}")
    
        # else:
        #     print(f"Not entering market from STRAT: {self.tick}")







