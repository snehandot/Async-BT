from backtesting import Strategy

class BaseStrategy(Strategy):
    def log_trade(self, action, price):
        print(f"{action} at {price}")