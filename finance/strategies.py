import alpaca_trade_api as tradeapi
import pandas as pd
from ta.momentum import RSIIndicator
from dotenv import load_dotenv
import os

load_dotenv()
alpaca_key = os.getenv("alpaca_api_key")
api_secret = os.getenv("alpaca_secret_key")


class MeanReversion:
    def __init__(
        self,
        api_key: str = alpaca_key,
        api_secret: str = api_secret,
        base_url: str = "https://paper-api.alpaca.markets",
        target_allocations: dict[str, float] = {"SPY": 0.4, "TQQQ": 0.3, "UVXY": 0.3},
    ):
        self.api: tradeapi.REST = tradeapi.REST(api_key, api_secret, base_url=base_url)
        self.target_allocations: dict = target_allocations

    def calculate_rsi(self, data, window=10):
        return RSIIndicator(data["close"], window).rsi()

    def calculate_sma(self, data, window=200):
        return data["close"].rolling(window=window).mean()

    def get_data(self, symbol, start_date, end_date):
        return self.api.get_barset(symbol, "day", start=start_date, end=end_date).df[
            symbol
        ]

    def rebalance(self):
        for symbol in self.target_allocations:
            position = self.api.get_position(symbol)
            value = float(position.qty) * float(position.current_price)
            target_value = self.api.get_account().cash * self.target_allocations[symbol]
            if abs(value - target_value) / self.api.get_account().cash > 0.1:
                self.api.submit_order(
                    symbol=symbol,
                    qty=int(target_value / float(position.current_price)),
                    side="buy" if value < target_value else "sell",
                    type="market",
                    time_in_force="gtc",
                )

    def execute(self, start_date, end_date):
        spy_data = self.get_data("SPY", start_date, end_date)
        tqqq_data = self.get_data("TQQQ", start_date, end_date)

        spy_sma = self.calculate_sma(spy_data)
        tqqq_rsi = self.calculate_rsi(tqqq_data)

        self.rebalance()

        if spy_data["close"].iloc[-1] > spy_sma.iloc[-1]:
            if tqqq_rsi.iloc[-1] > 79:
                self.api.submit_order(
                    symbol="UVXY",
                    qty=int(
                        self.api.get_account().cash
                        / self.api.get_last_trade("UVXY").price
                    ),
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
            else:
                self.api.submit_order(
                    symbol="TQQQ",
                    qty=int(
                        self.api.get_account().cash
                        / self.api.get_last_trade("TQQQ").price
                    ),
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
        else:
            if tqqq_rsi.iloc[-1] > 79:
                self.api.submit_order(
                    symbol="SPY",
                    qty=int(
                        self.api.get_account().cash
                        / self.api.get_last_trade("SPY").price
                    ),
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
            else:
                self.api.submit_order(
                    symbol="TQQQ",
                    qty=int(
                        self.api.get_account().cash
                        / self.api.get_last_trade("TQQQ").price
                    ),
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
