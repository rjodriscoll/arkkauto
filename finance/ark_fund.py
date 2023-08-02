from dataclasses import dataclass
from ticker import Ticker
import pandas as pd

@dataclass
class ArkAsset:
    ticker_symbol: str
    ticker: Ticker
    weight: float


@dataclass
class ArkFund:
    portfolio: list[ArkAsset]

    def __init__(self):
        self.portfolio: list = []
        self.weight_col: str = "weight  (%)"
        self.ticker_col: str = "ticker"

    def add_asset(self, asset: ArkAsset):
        self.portfolio.append(asset)

    def build_portfolio(self, data: pd.DataFrame):
        """data is expected to be the shape of holdings csvs, provided by"""
        data = data[~data[self.ticker_col].isna()]
        weights = data[self.weight_col].str[:-1].astype(float).values
        tickers = data[self.ticker_col].values
        for i, t in enumerate(tickers):
            t = self.clean_ticker(t)
            self.add_asset(ArkAsset(t, Ticker(t), weights[i]))

    @staticmethod
    def clean_ticker(ticker: str) -> str:
        if " " in ticker:
            return ticker.split(" ")[0]
        return ticker