from . import MarketBase, PositionBase
from .cost_engine import CostEngine
from ..balances import Balances

class SpotPosition (PositionBase):
    def __init__(self, market: "Spot", entry_price: float, balances: Balances) -> None:
        super().__init__(market, entry_price, balances)

    def get_open_size(self) -> float:
        # Returns the opened size of the position
        return self.balances.get_size(self.market.base)

class Spot (MarketBase):
    # Base/Quote spot market
    # * sizes are denominated in base currency

    def __init__(self, base: str, quote: str) -> None:
        self.base = base
        self.quote = quote

        MarketBase.__init__(self)
    
    def get_ticker(self) -> str:
        return f"{self.base}/{self.quote}"

    def get_funding_currency(self) -> str:
        # Returns the ticker for the funding currency for the market.
        return self.quote

    def get_contra_position_size(self, size: float, transact_cost_engine: CostEngine) -> float:
        """ Returns the contra-position size to close @param size of an exisiting position.

        @param size (float): The size of the existing position to close.
        @param transact_cost_engine (CostEngine): The transaction cost engine to use.

        @returns contra_size (float): The contra-position size adjusted for transaction costs.
        """
        if size == 0:
            return 0
        
        if size > 0:
            # Short contra-position (to offset an existing long-position)
            # - no adjustments for transaction cost required since transaction costs
            #       are incurred against quote currency.
            return -size

        # Contra_size function
        # 1. min_cost_size = -(abs(size) + min_cost)
        #       = size - min_cost
        # 2. running_cost_size = -(abs(size) / (1 - percent_cost_rate) + flat_cost)
        #       = size / (1 - percent_cost_rate) - flat_cost
        return min(
            size - transact_cost_engine.get_min_cost(),
            size / (1. - transact_cost_engine.get_percent_cost_rate()) - transact_cost_engine.get_flat_cost()
        )

    def make_cost_position(self, cost: float) -> PositionBase:
        cost_balances = Balances()
        cost_balances.add_balance(self.quote, -cost)

        return SpotPosition(self, 0, cost_balances)

    def open_position(self, price: float, size: float, transact_cost_engine: CostEngine) -> PositionBase:
        """ Opens a market position. To close an existing position use @close_position.

        @param price (float): The average price of the position to open.
        @param size (float): The number of contracts or size of position to open, where
                negative sizes indicate a short position.
        @param transact_cost_engine (CostEngine): The transaction cost engine to use.

        @returns opened_position (PositionBase): The position generated from the transaction.
        """
        position_balances = Balances()

        if size > 0: # Long position: transaction costs incurred against base currency
            position_balances.add_balance(self.base, size - transact_cost_engine
                    .get_fill_cost(price * size) / price)
            
            position_balances.add_balance(self.quote, -(price * size))
        elif size < 0: # Short position: transaction costs incurred against quote currency
            position_balances.add_balance(self.base, size)
            position_balances.add_balance(self.quote, price * abs(size) - transact_cost_engine
                    .get_fill_cost(price * size))

        return SpotPosition(self, price, position_balances)

    def close_position(self, price: float, size: float, transact_cost_engine: CostEngine) -> PositionBase:
        """ Closes an existing market position of @param size.

        @param price (float): The average price to close the position at.
        @param size (float): The number of contracts or size of position to close, where
                negative sizes indicate an exisiting short position.
        @param transact_cost_fn (CostFunctionBase): The transaction cost function to apply.

        @returns closed_position (PositionBase): The position generated from the transaction.
                Execute Portfolio.assimilate(closed_position) to offset and close the
                exisiting position.
        """
        contra_size = self.get_contra_position_size(size, transact_cost_engine)

        if size > 0:
            return self.open_position(price, contra_size, transact_cost_engine)

        position_balances = Balances()
        position_balances.add_balance(self.base, abs(size))
        position_balances.add_balance(self.quote, -(price * contra_size))

        return SpotPosition(self, price, position_balances)

if __name__ == "__main__":
    pass
