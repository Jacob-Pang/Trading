from datetime import datetime

from . import MarketPosition
from .derivative import DerivativeMarketBase
from ..portfolio import Portfolio
from ..portfolio.balance import AssetBalance
from ..portfolio.balance.option import CallOptionBalance, PutOptionBalance
from ..market_listener import MarketListenerBase

class OptionMarketBase (DerivativeMarketBase):
    def __init__(self, option_ticker: str, quote_ticker: str, asset_ticker: str,
        strike_price: float, expiry_datetime: (float | datetime), base_market_listener:
        MarketListenerBase = None, quote_market_listener: MarketListenerBase = None) -> None:

        DerivativeMarketBase.__init__(self, option_ticker, quote_ticker, asset_ticker,
                base_market_listener, quote_market_listener, expiry_datetime)
        
        self.strike_price = strike_price

    @property
    def option_ticker(self) -> str:
        return self.base_ticker

    def make_position(self, base_size: float, quote_size: float) -> MarketPosition:
        raise NotImplementedError()

class CallOptionMarket (OptionMarketBase):
    def make_position(self, base_size: float, quote_size: float) -> MarketPosition:
        quote_entry_price = self.quote_current_price
        base_entry_price = abs(quote_size * quote_entry_price / base_size) \
                if base_size else quote_entry_price

        position_portfolio = Portfolio()
        position_portfolio.add(CallOptionBalance(base_size, base_entry_price, self.asset_ticker,
                self.strike_price, self.expiry_datetime, self.option_ticker))
        position_portfolio.add(AssetBalance(quote_size, quote_entry_price, self.quote_ticker))

        return MarketPosition(self, position_portfolio)

class PutOptionMarket (OptionMarketBase):
    def make_position(self, base_size: float, quote_size: float) -> MarketPosition:
        quote_entry_price = self.quote_current_price
        base_entry_price = abs(quote_size * quote_entry_price / base_size) \
                if base_size else quote_entry_price

        position_portfolio = Portfolio()
        position_portfolio.add(PutOptionBalance(base_size, base_entry_price, self.asset_ticker,
                self.strike_price, self.expiry_datetime, self.option_ticker))
        position_portfolio.add(AssetBalance(quote_size, quote_entry_price, self.quote_ticker))

        return MarketPosition(self, position_portfolio)

if __name__ == "__main__":
    pass