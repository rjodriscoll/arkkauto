import alpaca_trade_api as tradeapi
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from utils import alpaca_keys
from datetime import datetime, timedelta
from yahooquery import Ticker as YQTicker
from itertools import chain
import statistics
import yfinance as yf
from dateutil.relativedelta import relativedelta

alpaca_key, alpaca_secret = alpaca_keys()


class Ticker:
    def __init__(
        self,
        symbol,
        api_key=alpaca_key,
        api_secret=alpaca_secret,
        base_url="https://paper-api.alpaca.markets",
        end_date=datetime.now(),
        start_date=datetime.now() - timedelta(days=365),
    ):
        self.symbol = symbol
        self.api = tradeapi.REST(api_key, api_secret, base_url=base_url)
        self.data = self.get_data()
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.get_data()
        self.company_info = self.get_company_info()
        self.yf_info = self.get_yf_info()

    def get_data(self):
        return self.api.get_barset(
            self.symbol, "day", start=self.start_date, end=self.end_date
        ).df[self.symbol]

    def get_company_info(self):
        return self.api.polygon.company(self.symbol)

    def get_yf_info(self):
        return yf.Ticker(self.symbol).info

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

    @property
    def peg_ratio(self):
        return self.yf_info["pegRatio"]

    @property
    def ps_ratio(self):
        return self.yf_info["priceToSalesTrailing12Months"]

    @property
    def pb_ratio(self):
        return self.yf_info["priceToBook"]

    @property
    def dividend_yield(self):
        return self.yf_info["dividendYield"]

    @property
    def debt_to_equity(self):
        return self.yf_info["debtToEquity"]

    @property
    def return_on_equity(self):
        return self.yf_info["returnOnEquity"]

    @property
    def eps(self):
        return self.yf_info["trailingEps"]

    @property
    def current_ratio(self):
        return self.yf_info["currentRatio"]

    @property
    def beta(self):
        return self.yf_info["beta"]

    @property
    def mean_recommendation(self):
        df = YQTicker(self.symbol).recommendation_trend.reset_index()
        mean_values = {}
        for period in df["period"].unique():
            ratings = df[df["period"] == period]
            l = [
                [1] * ratings.strongBuy.values[0],
                [2] * ratings.buy.values[0],
                [3] * ratings.hold.values[0],
                [4] * ratings.sell.values[0],
                [5] * ratings.strongSell.values[0],
            ]
            mean_value = statistics.mean(list(chain(*l)))
            if period == "0m":
                period = datetime.now().strftime("%Y-%m")
            else:
                # Subtract the number of months from the current date
                period = (
                    datetime.now() - relativedelta(months=int(period[:-1]))
                ).strftime("%Y-%m")
            mean_values[period] = mean_value
        return mean_values
