from binance.client import Client
from config.config import API_KEY, API_SECRET, BASE_URL, CB_API_KEY , CB_API_SECRET
from coinbase.rest import RESTClient
from json import dumps
import time
import hmac
import hashlib
import requests
import pandas as pd
from urllib.parse import urlencode
from config.config import API_KEY, API_SECRET, BASE_URL
import aiohttp
from decimal import Decimal



class REST_Binance:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET.encode()
        self.base_url = BASE_URL.rstrip('/')

    def _headers(self):
        return {
            'X-MBX-APIKEY': self.api_key
        }

    def _sign(self, params):
        query_string = urlencode(params)
        signature = hmac.new(self.api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        params['signature'] = signature
        return params

    async def order(self, symbol, side, size,session, quote_order_qty=None):
        url = f"{self.base_url}/v3/order/test"
        
        # if not quantity and not quote_order_qty:
        #     print("333")
        #     raise ValueError("Either 'quantity' or 'quote_order_qty' must be specified")

        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'MARKET',
            'timestamp': int(time.time() * 1000)
        }


        params['quantity'] = size
        print(params['quantity'])
        signed_params = self._sign(params)

        async with session.post(url, headers=self._headers(), params=signed_params) as response:
            try:
                data = await response.json()
            except Exception:
                text = await response.text()
                raise Exception(f"Failed to decode response. Status: {response.status}, Body: {text}")

            if response.status != 200:
                print("444")
                raise Exception(f"Order rejected. Status: {response.status}, Error: {data}")

            return data

    async def fetch_ohlcv(self, session, symbol, interval='1m', limit=100):
        url = f"{self.base_url}/v3/klines"
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': limit
        }

        async with session.get(url, params=params) as response:
            if response.status != 200:
                data = await response.json()
                raise Exception(f"OHLCV fetch failed: {data}")
            
            klines = await response.json()

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


class SDK_Binance:
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

        
class REST_Coinbase:
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
