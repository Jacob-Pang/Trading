from .cost_engine import CostEngine
from ..balances import Balances

class PositionBase:
    def __init__(self, market: "MarketBase", entry_price: float, balances: Balances) -> None:
        self.market = market
        self.avg_price = entry_price
        self.balances = balances

    @property
    def open(self) -> bool:
        # Margin of error for floating point arithmetic errors
        return abs(self.get_open_size()) > 0.0001

    @property
    def closed(self) -> bool:
        return not self.open

    @property
    def short(self) -> bool:
        # Returns whether the position is a short one
        return self.get_open_size() < 0

    def assimilate(self, other_position: "PositionBase") -> None:
        open_size = self.get_open_size()
        other_size = other_position.get_open_size()
        net_size = open_size + other_size
        
        self.avg_price = (self.avg_price * open_size + other_position.avg_price * other_size) \
                / (open_size + other_size) if net_size else None

        self.balances.assimilate(other_position.balances)
        
    def get_open_size(self) -> float:
        # Returns the opened size of the position
        raise NotImplementedError()

    def get_closing_size(self, trasact_cost_engine: CostEngine) -> float:
        # Returns the size to close this position accounting for transaction fees
        return self.market.get_contra_position_size(self.get_open_size(), trasact_cost_engine)

class MarketBase:
    def __init__(self) -> None:
        # Reduce overhead by caching the attributes
        self.ticker = self.get_ticker()
        self.query = self.get_query()

    # Getters
    def get_ticker(self) -> str:
        raise NotImplementedError()

    def get_query(self) -> str:
        # Returns the query string for the URL
        return None

    def get_funding_currency(self) -> str:
        # Returns the ticker for the funding currency for the market.
        raise NotImplementedError()

    def get_contra_position_size(self, size: float, transact_cost_engine: CostEngine) -> float:
        """ Returns the contra-position size to close @param size of an exisiting position.

        @param size (float): The size of the existing position to close.
        @param transact_cost_engine (CostEngine): The transaction cost engine to use.

        @returns contra_size (float): The contra-position size adjusted for transaction costs.
        """
        return -size

    # Position generators
    def make_empty_position(self) -> PositionBase:
        return self.open_position(0, 0, None)

    def make_cost_position(self, cost: float) -> PositionBase:
        raise NotImplementedError()

    # Actors
    def open_position(self, price: float, size: float, transact_cost_engine: CostEngine) -> PositionBase:
        """ Opens a market position. To close an existing position use @close_position.

        @param price (float): The average price of the position to open.
        @param size (float): The number of contracts or size of position to open, where
                negative sizes indicate a short position.
        @param transact_cost_engine (CostEngine): The transaction cost engine to use.

        @returns opened_position (PositionBase): The position generated from the transaction.
        """
        raise NotImplementedError()

    def close_position(self, price: float, size: float, transact_cost_engine: CostEngine) -> PositionBase:
        """ Closes an existing market position of @param size.

        @param price (float): The average price of the position to open.
        @param size (float): The number of contracts or size of position to open, where
                negative sizes indicate a short position.
        @param transact_cost_engine (CostEngine): The transaction cost engine to use.

        @returns closed_position (PositionBase): The position generated from the transaction.
                Execute Portfolio.assimilate(closed_position) to offset and close the
                exisiting position.
        """
        raise NotImplementedError()

if __name__ == "__main__":
    pass
