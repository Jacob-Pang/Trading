from datetime import datetime

from . import MarketBase, MarketPosition
from .cost_engine import CostEngine
from ..portfolio import Portfolio
from ..portfolio.balance import AssetBalance
from ..portfolio.balance.derivative import DerivativeBalance
from ..market_listener import MarketListenerBase

class DerivativeMarketBase (MarketBase):
    # Implements an abstract spot market
    def __init__(self, derivative_ticker: str, quote_ticker: str, asset_ticker: str,
        base_market_listener: MarketListenerBase = None, quote_market_listener:
        MarketListenerBase = None, expiry_datetime: (float | datetime) = None) -> None:

        MarketBase.__init__(self, derivative_ticker, quote_ticker, base_market_listener,
                quote_market_listener)
        
        self.asset_ticker = asset_ticker
        self.expiry_datetime: float = expiry_datetime.timestamp() \
                if isinstance(expiry_datetime, datetime) else \
                expiry_datetime
    
    @property
    def derivative_ticker(self) -> str:
        return self.base_ticker

    # Getters
    def get_contra_position_size(self, size: float, transact_cost_engine: CostEngine = CostEngine()) \
        -> float:
        """ Returns the contra-position size to close @param size of an exisiting position.

        @param size (float): The size of the existing position to close.
        @param transact_cost_engine (CostEngine, opt): The transaction cost engine to use.

        @returns contra_size (float): The contra-position size adjusted for transaction costs.
        """
        return -size

    # Actors
    def make_position(self, base_size: float, quote_size: float) -> MarketPosition:
        quote_entry_price = self.quote_current_price
        base_entry_price = abs(quote_size * quote_entry_price / base_size) \
                if base_size else quote_entry_price

        position_portfolio = Portfolio()
        position_portfolio.add(DerivativeBalance(base_size, base_entry_price, self.asset_ticker,
                self.expiry_datetime, self.derivative_ticker))
        position_portfolio.add(AssetBalance(quote_size, quote_entry_price, self.quote_ticker))

        return MarketPosition(self, position_portfolio)

    def open_position(self, entry_price: float, size: float, transact_cost_engine: CostEngine
        = CostEngine()) -> MarketPosition:
        """ Opens a market position. To close an existing position use @close_position.

        @param entry_price (float): The average price to enter the position at.
        @param size (float): The number of contracts or size of position to open, where
                negative sizes indicate a short position.
        @param transact_cost_engine (CostEngine, opt): The transaction cost engine to use.

        @returns opened_position (PositionBase): The position generated from the transaction.
        """
        return self.make_position(size, -(entry_price * size + transact_cost_engine
                .get_fill_cost(entry_price * size)))

    def close_position(self, exit_price: float, size: float, transact_cost_engine: CostEngine
        = CostEngine()) -> MarketPosition:
        """ Closes an existing market position of @param size.

        @param exit_price (float): The average price to exit the position at.
        @param size (float): The number of contracts or size of position to open, where
                negative sizes indicate a short position.
        @param transact_cost_engine (CostEngine, opt): The transaction cost engine to use.

        @returns closed_position (PositionBase): The position generated from the transaction.
                Execute Portfolio.assimilate(closed_position) to offset and close the
                exisiting position.
        """
        return self.open_position(exit_price, self.get_contra_position_size(size,
                transact_cost_engine), transact_cost_engine)

if __name__ == "__main__":
    pass
