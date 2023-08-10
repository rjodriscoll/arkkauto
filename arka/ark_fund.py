from dataclasses import dataclass
from arka.ticker import Ticker
import pandas as pd
from tqdm import tqdm
from enum import Enum


@dataclass
class ArkAsset:
    ticker_symbol: str
    ticker: Ticker
    weight: float
    price: float


@dataclass
class Action:
    action: str
    percentage_adjustment: float
    ticker: str


class ActionType(Enum):
    BUY = "Buy"
    SELL = "Sell"


@dataclass
class WeightDiff:
    weight_diff: float


class Fund:
    portfolio: list[ArkAsset]

    def __init__(self):
        self.portfolio: list = []
        self.weight_col: str = "weight  (%)"
        self.ticker_col: str = "ticker"

    def add_asset(self, asset: ArkAsset):
        self.portfolio.append(asset)

    def build_portfolio(self, data: pd.DataFrame):
        """data is expected to be the shape of holdings csvs, provided by ark"""
        data = data[~data[self.ticker_col].isna()]
        weights = data[self.weight_col].str[:-1].astype(float).values
        tickers = data[self.ticker_col].values
        for i, t in tqdm(
            enumerate(tickers), total=len(tickers), desc="Building portfolio"
        ):
            t = self.clean_ticker(t)
            tick = Ticker(t)
            self.add_asset(ArkAsset(t, tick, weights[i], tick.current_price))
        self.portfolio_as_dict()

    def portfolio_as_dict(self):
        self.portfolio_dict = {
            asset.ticker_symbol: WeightDiff(asset.weight)
            for asset in self.portfolio
        }

    @staticmethod
    def clean_ticker(ticker: str) -> str:
        if " " in ticker:
            return ticker.split(" ")[0]
        return ticker


class PortfolioComparator:
    def __init__(
        self,
        true_portfolio: dict[str, WeightDiff],
        target_portfolio: dict[str, WeightDiff],
        min_threshold: float = 0.1,
    ):
        self.true_portfolio = true_portfolio
        self.target_portfolio = target_portfolio
        self.min_threshold = min_threshold

    def compare(self) -> dict[str, WeightDiff]:
        all_keys = set(self.true_portfolio.keys()).union(
            set(self.target_portfolio.keys())
        )
        difference = {}
        for key in all_keys:
            true_diff = self.true_portfolio.get(key, WeightDiff(0))
            target_diff = self.target_portfolio.get(key, WeightDiff(0))
            difference[key] = WeightDiff(
                true_diff.weight_diff - target_diff.weight_diff,
            )
        return difference

    def get_action(self, ticker: str, values: WeightDiff) -> Action:
        weight_diff = round(values.weight_diff, 2)
        if abs(weight_diff) > self.min_threshold:
            action_type = ActionType.BUY if weight_diff > 0 else ActionType.SELL
            action = Action(
                action_type.value,
                abs(weight_diff),
                ticker,
            )
            return action

    def balance_actions(self) -> list[Action]:
        actions = []
        for ticker, values in self.compare().items():
            action = self.get_action(ticker, values)
            if action is not None:
                actions.append(action)
        return actions
