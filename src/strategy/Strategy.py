import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.trading.exchange import REST_Binance,SDK_Binance,REST_Coinbase
from config.config import SYMBOL, TRADE_QTY

class Strategy:
    def __init__(self,tick,session):
        # self.func=None
        self.symbol=tick
        self.session=session
        self.broker=REST_Binance()
        self.pos=1


    @property
    async def data_1s(self):
        df = await self.broker.fetch_ohlcv(symbol=self.symbol, interval="1s", limit=50,session=self.session)
        return df
    @property
    async def data_1m(self):
        df = await self.broker.fetch_ohlcv(symbol=self.symbol, interval="1m", limit=50,session=self.session)
        return df
        
    async def buy(self,size=TRADE_QTY):
        print(SYMBOL,size)
        order = await self.broker.order(self.symbol,"BUY",size,self.session)
        return
        
    async def sell(self,size=TRADE_QTY):
        order = await self.broker.order(self.symbol,"SELL",size,self.session)
        return
    
    

        