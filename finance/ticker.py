import alpaca_trade_api as tradeapi
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from utils import alpaca_keys

alpaca_key, alpaca_secret = alpaca_keys()


class Ticker:
    def __init__(
        self,
        symbol,
        api_key=alpaca_key,
        api_secret=alpaca_secret,
        base_url="https://paper-api.alpaca.markets",
    ):
        self.symbol = symbol
        self.api = tradeapi.REST(api_key, api_secret, base_url=base_url)
        self.data = self.get_data()

    def get_data(self, start_date="2022-01-01", end_date="2023-01-01"):
        return self.api.get_barset(
            self.symbol, "day", start=start_date, end=end_date
        ).df[self.symbol]

    @property
    def rsi(self, window=10):
        return RSIIndicator(self.data["close"], window).rsi()

    @property
    def sma(self, window=200):
        return SMAIndicator(self.data["close"], window).sma_indicator()
