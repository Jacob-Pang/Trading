from . import MarketBase, PositionBase
from .cost_engine import CostEngine
from ..balances import Balances

class DerivativePosition (PositionBase):
    def __init__(self, market: "Derivative", entry_price: float, balances: Balances) -> None:
        super().__init__(market, entry_price, balances)

    def get_open_size(self) -> float:
        # Returns the opened size of the position
        return self.balances.get_size(self.market.ticker)

class Derivative (MarketBase):
    def __init__(self, ticker: str, settlement_ticker: str) -> None:
        self.ticker = ticker
        self.settlement_ticker = settlement_ticker
        
        MarketBase.__init__(self)

    def get_ticker(self) -> str:
        return self.ticker

    def get_settlement_ticker(self) -> str:
        # Returns the ticker for the funding currency for the market.
        raise self.settlement_ticker

    def make_cost_position(self, cost: float) -> PositionBase:
        cost_balances = Balances()
        cost_balances.add_balance(self.settlement_ticker, -cost)

        return DerivativePosition(self, 0, cost_balances)

    def open_position(self, price: float, size: float, transact_cost_engine: CostEngine) -> PositionBase:
        """ Opens a market position. To close an existing position use @close_position.

        @param price (float): The average price of the position to open.
        @param size (float): The number of contracts or size of position to open, where
                negative sizes indicate a short position.
        @param transact_cost_engine (CostEngine): The transaction cost engine to use.

        @returns opened_position (PositionBase): The position generated from the transaction.
        """        
        position_balances = Balances()
        position_balances.add_cfd_balance(self.ticker, self.settlement_ticker, size, price)
        position_balances.add_balance(self.settlement_ticker, -transact_cost_engine
                .get_fill_cost(price * size))

        return DerivativePosition(self, price, position_balances)

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
        return self.open_position(price, self.get_contra_position_size(size, transact_cost_engine),
                transact_cost_engine)

if __name__ == "__main__":
    pass