import alpaca_trade_api as tradeapi
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
        end_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') ,
        start_date=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    ):
        self.symbol = symbol
        self.api = tradeapi.REST(
            key_id=api_key, secret_key=api_secret, base_url=base_url
        )
        self.start_date = start_date # - 1 here because of rate limits
        self.end_date = end_date
        self.data = self.get_data()
        self.yf_info = self.get_yf_info()

    def get_data(self):
        return self.api.get_bars(
            self.symbol, "1D", start=self.start_date, end=self.end_date
        ).df.reset_index()

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
        return self.yf_info["marketCap"]

    @property
    def pe_ratio(self):
        return self.yf_info["trailingPE"]

    @property
    def peg_ratio(self):
        return self.yf_info["pegRatio"]

    @property
    def pb_ratio(self):
        return self.yf_info["priceToBook"]

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
    def current_price(self):
        return self.data.iloc[-1]["close"]
    
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
                    datetime.now() + relativedelta(months=int(period[:-1]))
                ).strftime("%Y-%m")
            mean_values[period] = mean_value
        return mean_values
