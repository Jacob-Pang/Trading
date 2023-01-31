from .cost_engine import CostEngine
from ..portfolio import Portfolio
from ..portfolio.balance import AssetBalance
from ..market_listener import MarketListenerBase

class MarketPosition:
    def __init__(self, market: "MarketBase", portfolio: Portfolio) -> None:
        self.market = market
        self.portfolio = portfolio

    @property
    def avg_price(self) -> float:
        return self.portfolio.get_balance(self.market.base_ticker).entry_price

    @property
    def open_size(self) -> float:
        # Returns the opened size of the position
        return self.portfolio.get_size(self.market.base_ticker)

    @property
    def open(self) -> bool:
        # Allow margin of error for floating point arithmetic errors
        return abs(self.open_size) > 0.0001

    @property
    def closed(self) -> bool:
        return not self.open

    @property
    def short(self) -> bool:
        # Returns whether the position is a short one
        return self.open_size < 0

    def __repr__(self) -> str:
        return self.portfolio.__repr__()

    # Getters
    def get_value(self, current_price: float) -> float:
        # Returns the current value of the position in quote currency terms
        return self.portfolio.get_value({
            self.market.base_ticker: current_price,
            self.market.quote_ticker: 1
        })

    def get_closing_size(self, transact_cost_engine: CostEngine) -> float:
        # Returns the size to close this position accounting for transaction fees
        return self.market.get_contra_position_size(self.open_size, transact_cost_engine)

    # Mutators
    def assimilate(self, other_position: "MarketPosition") -> None:
        self.portfolio.assimilate(other_position.portfolio)

class MarketBase:
    # Implements an abstract spot market
    def __init__(self, base_ticker: str, quote_ticker: str, base_market_listener:
        MarketListenerBase = None, quote_market_listener: MarketListenerBase = None) -> None:
        self.base_ticker = base_ticker
        self.quote_ticker = quote_ticker
        self.base_market_listener = base_market_listener
        self.quote_market_listener = quote_market_listener

    @property
    def quote_current_price(self) -> float:
        if self.quote_market_listener:
            return self.quote_market_listener.get_current_price()

        return 1
    
    # Getters
    def get_market_listener(self) -> MarketListenerBase:
        return self.base_market_listener

    def get_contra_position_size(self, size: float, transact_cost_engine: CostEngine = CostEngine()) \
        -> float:
        """ Returns the contra-position size to close @param size of an exisiting position.

        @param size (float): The size of the existing position to close.
        @param transact_cost_engine (CostEngine, opt): The transaction cost engine to use.

        @returns contra_size (float): The contra-position size adjusted for transaction costs.
        """
        # Short contra-position (to offset an existing long-position)
        # * no adjustments for transaction cost required since transaction costs
        #       are incurred against quote currency.
        if size >= 0:   return -size
                    
        # Contra_size function
        # 1. min_cost_size = (abs(size) + min_cost)
        #       = min_cost - size
        # 2. running_cost_size = (abs(size) / (1 - percent_cost_rate) + flat_cost)
        #       = flat_cost - size / (1 - percent_cost_rate)
        return max(
            transact_cost_engine.get_min_cost() - size,
            transact_cost_engine.get_flat_cost() - size / (1. - transact_cost_engine
                    .get_variable_cost_rate())
        )

    # Actors
    def make_position(self, base_size: float, quote_size: float) -> MarketPosition:
        quote_entry_price = self.quote_current_price
        base_entry_price = abs(quote_size * quote_entry_price / base_size) \
                if base_size else quote_entry_price

        position_portfolio = Portfolio()
        position_portfolio.add(AssetBalance(base_size, base_entry_price, self.base_ticker))
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
        base_size, quote_size = ( # Long position: transaction costs incurred against base currency
            size - transact_cost_engine.get_fill_cost(entry_price * size) / entry_price,
            -(entry_price * size)
        ) if size > 0 else ( # Short position: transaction costs incurred against quote currency
            size,
            -(entry_price * size + transact_cost_engine.get_fill_cost(entry_price * size))
        )

        return self.make_position(base_size, quote_size)

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
        contra_size = self.get_contra_position_size(size, transact_cost_engine)

        if size > 0:
            return self.open_position(exit_price, contra_size, transact_cost_engine)

        return self.make_position(-size, -(exit_price * contra_size))

    # Position generators
    def make_empty_position(self) -> MarketPosition:
        return self.open_position(0, 0, CostEngine())

    def make_cost_position(self, cost: float) -> MarketPosition:
        # Creates a cost (settlement currency-based) position
        cost_portfolio = Portfolio()
        cost_portfolio.add(AssetBalance(-cost, self.quote_current_price, self.quote_ticker))

        return MarketPosition(self, cost_portfolio)

if __name__ == "__main__":
    pass
