from binance.client import Client
from config.config import API_KEY, API_SECRET, BASE_URL, CB_API_KEY , CB_API_SECRET
from coinbase.rest import RESTClient
from json import dumps

class Broker:
    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)
        self.client.API_URL = BASE_URL
    
    # def place_test_order(symbol, side, quantity):
    #     return client.create_test_order(
    #         symbol=symbol,
    #         side=side,
    #         type='MARKET',
    #         quantity=quantity
    #     )
    def order(self,symbol,side,quantity):
        if side=="BUY":
            order = self.client.order_market_buy(
            symbol=symbol,
            quantity=quantity)
        else:
            order = self.client.order_market_sell(
            symbol=symbol,
            quantity=quantity)
        return order
        
    def fetch_ohlcv(symbol, interval, limit):
        import pandas as pd
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    
        df = pd.DataFrame(klines, columns=[
            'time', 'o', 'h', 'l', 'c', 'v',
            'close_time', 'quote_volume', 'num_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
    
        df['Date'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('Date', inplace=True)
        df = df.astype({'o': float, 'h': float, 'l': float, 'c': float, 'v': float})
        df.rename(columns={
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume'
        }, inplace=True)
    
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

        
class Coinbase:
    def __init__(self):
        self.client = RESTClient(api_key=CB_API_KEY, api_secret=CB_API_SECRET,base_url="https://api-sandbox.coinbase.com/api/v3/brokerage/orders")
        self.accounts = self.client.get_accounts()
        print(dumps(accounts.to_dict(), indent=2))
    def order(self,symbol,side,quantity):
        if side=="BUY":
            print("Bought")
            order = client.preview_market_order_buy(
            client_order_id="00234",
            product_id="BTC-USD",
            quote_size="10"
             )
        
            if order['success']:
                order_id = order['success_response']['order_id']
                fills = client.get_fills(order_id=order_id)
                print(json.dumps(fills.to_dict(), indent=2))
            else:
                error_response = order['error_response']
                print(error_response)
        else:
            print("Sell")
            pass
