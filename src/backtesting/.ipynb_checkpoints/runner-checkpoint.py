import pandas as pd
import matplotlib.pyplot as plt
import asyncio

class Backtest:
    def __init__(self, data1_list, data2_list, strat_class, cash):
        self.cash = cash
        self.strat_class = strat_class
        self.data1_list = data1_list
        self.data2_list = data2_list
        self.trades_list = []

    def execute(self):
        data1 = self.data1_list[0]
        data2 = self.data2_list[0]
        strategy = self.strat_class(data1, data2)
        for i in range(1, len(data1)):
            print(f"Sync step {i}/{len(data1)}", end="\r")
            strategy.next(0)
        self.trades_list = [strategy.trades]

    async def _run_strategy(self, idx: int):
        data1 = self.data1_list[idx]
        data2 = self.data2_list[idx]
        strategy = self.strat_class(data1, data2)
        total = len(data1)
        print(f"strategy {idx} start")
        for i in range(1, total):
            if i % 100 == 0:
                await asyncio.sleep(0) 
            strategy.next(idx)
        print(f"Strategy {idx} finish ")
        return strategy.trades

    def execute_async(self):
        async def _execute_all():
            tasks = [asyncio.create_task(self._run_strategy(i)) for i in range(len(self.data1_list))]
            return await asyncio.gather(*tasks)

        self.trades_list = asyncio.run(_execute_all())

    def run(self):
        all_stats = []
        for i, trades in enumerate(self.trades_list):
            df = pd.DataFrame(trades)
            df['side'] = df['action'].map({'BUY': 1, 'SELL': -1})
            df['pnl'] = df['price'].diff() * df['side'] * df['size']
            df['pnl'].iloc[0] = 0
            print(f"[Strategy {i}] Total Returns:", df['pnl'].sum())
            all_stats.append(df)
        return all_stats

    def plot(self, index=0, figsize=(12, 6)):
        if not self.trades_list:
            print("No trades found. Run execute_async() or execute() first.")
            return

        trades = pd.DataFrame(self.trades_list[index])
        price = self.data1_list[index]['Close']

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(price.index, price.values, label='Price')

        buys = trades[trades['action'] == 'BUY']
        sells = trades[trades['action'] == 'SELL']

        ax.scatter(buys['time'], buys['price'], marker='^', s=100, label='BUY')
        ax.scatter(sells['time'], sells['price'], marker='v', s=100, label='SELL')

        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.set_title(f'Backtest {index}: Buy/Sell Signals')
        ax.legend()
        plt.tight_layout()
        plt.show()