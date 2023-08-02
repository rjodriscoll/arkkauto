import alpaca_trade_api as tradeapi
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from utils import alpaca_keys
from datetime import datetime, timedelta
alpaca_key, alpaca_secret = alpaca_keys()


class Ticker:
    def __init__(
        self,
        symbol,
        api_key=alpaca_key,
        api_secret=alpaca_secret,
        base_url="https://paper-api.alpaca.markets",
        end_date = datetime.now(),
        start_date = datetime.now() - timedelta(days=365)
    ):
        self.symbol = symbol
        self.api = tradeapi.REST(api_key, api_secret, base_url=base_url)
        self.data = self.get_data()
        self.start_date = start_date
        self.end_date = end_date
        self.company_info = self.get_company_info()

    def get_data(self):
        return self.api.get_barset(
            self.symbol, "day", start=self.start_date, end=self.end_date
        ).df[self.symbol]
    
    def get_company_info(self):
        return self.api.polygon.company(self.symbol)

    @property
    def rsi(self, window=10):
        return RSIIndicator(self.data["close"], window).rsi()

    @property
    def sma(self, window=200):
        return SMAIndicator(self.data["close"], window).sma_indicator()
    
    @property
    def market_cap(self):
        return self.company_info.marketcap

    @property
    def pe_ratio(self):
        return self.company_info.peratio

    