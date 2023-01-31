from datetime import datetime
from .derivative import DerivativeBalance
from ...price_model import PriceModelBase
from ...price_model.price_distribution.option import CallOptionPriceDistributionBase, \
        PutOptionPriceDistributionBase

class OptionBalance (DerivativeBalance):
    def __init__(self, size: float, entry_price: float, asset_ticker: str, strike_price: float,
        expiry_datetime: float, option_ticker: str = None) -> None:
        DerivativeBalance.__init__(self, size, entry_price, asset_ticker, expiry_datetime,
                option_ticker)

        self.strike_price = strike_price

class CallOptionBalance (OptionBalance):
    def get_price_dist(self, price_model: PriceModelBase) -> CallOptionPriceDistributionBase:
        return price_model.get_call_option_price_dist(self.asset_ticker, self.strike_price,
                price_model.get_time_to_expiry(self.expiry_datetime), self.ticker)

class PutOptionBalance (OptionBalance):
    def get_price_dist(self, price_model: PriceModelBase) -> PutOptionPriceDistributionBase:
        return price_model.get_put_option_price_dist(self.asset_ticker, self.strike_price,
                price_model.get_time_to_expiry(self.expiry_datetime), self.ticker)

if __name__ == "__main__":
    pass