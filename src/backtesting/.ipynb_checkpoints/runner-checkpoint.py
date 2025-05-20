import pandas as pd
import matplotlib.pyplot as plt
#pseudo code for backtest , 
class Backtest:
    def __init__(self,data1,data2,strat,cash):
        self.cash=cash
        self.strat_object=strat
        self.whole_data=data1
        self.hr_data=data2
        self.strategy=None

    def execute(self):
        self.multi_tf=self.strat_object(self.whole_data,self.hr_data)
        for i in range(1,250):#len(self.whole_data)):
            print(i,end="\r")
            self.multi_tf.next()
        
    def run(self):
        trades = pd.DataFrame(self.multi_tf.trades)
        trades['side'] = trades['action'].map({'BUY': 1, 'SELL': -1})
        trades['pnl']  = trades['price'].diff() * trades['side'] * trades['size']
        trades['pnl'].iloc[0] = 0  
        print("Total Returns for backtest:", trades['pnl'].sum())
        return trades        

    def plot(self, figsize=(12,6)):
        trades = pd.DataFrame(self.multi_tf.trades)
        print(trades)

        price = self.whole_data['Close']

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(price.index, price.values, label='Price')

        buys  = trades[trades['action'] == 'BUY']
        sells = trades[trades['action'] == 'SELL']

        ax.scatter(buys['time'],  buys['price'],
                   marker='^', s=100, color='blue',  label='BUY')
        ax.scatter(sells['time'], sells['price'],
                   marker='v', s=100, color='red',   label='SELL')

        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.set_title('Backtest: Buy/Sell Signals')
        ax.legend()
        plt.tight_layout()
        plt.show()
            

    
    # @property
    # def data(self):
    #     return self.data
        