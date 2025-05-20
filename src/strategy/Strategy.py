import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.trading.exchange import Broker
from config.config import SYMBOL, TRADE_QTY

class Strategy:
    def __init__(self,whole_data):
        # self.func=None
        # self.symbol=SYMBOL
        self.broker=Broker()
        self.whole_data=whole_data
        self.pos=1

    
    @property #Because in the main class , self.data is called without ()
    def data(self):
        # self.Close=
        self.Close=self.whole_data[:self.pos+1]
        self.pos+=1
        return self.Close
        
    def buy(self,size=TRADE_QTY):
        print(SYMBOL,size)
        order=self.broker.order(SYMBOL,"BUY",size)
        
    def sell(self,size=TRADE_QTY):
        order=self.broker.order(SYMBOL,"SELL",size)
    
    

        