from threading import Semaphore

from .portfolio import Portfolio
from .market import MarketBase, MarketPosition
from .market.cost_engine import CostEngine

class Order:
    def __init__(self, market: MarketBase, price: float, size: float, transact_cost_engine:
        CostEngine = CostEngine(), cancellation_cost: float = 0, parent_portfolio:
        Portfolio = None) -> None:

        self.market = market
        self.price = price
        self.size = size
        self.transact_cost_engine = transact_cost_engine
        self.cancellation_cost = cancellation_cost
        self.parent_portfolio = parent_portfolio
        self.filled_position = market.make_empty_position()

        self._semaphore = Semaphore(1)
        self._executed = False

    @property
    def filled(self) -> bool:
        return self.size == 0

    @property
    def short(self) -> bool:
        # Returns whether the order is for a short position
        return self.size < 0

    def has_filled(self) -> bool:
        # Predicate for property filled
        return self.filled

    def assimilate_filled(self, filled_position: MarketPosition) -> None:
        self.filled_position.assimilate(filled_position)

    def execute_order(self) -> None:
        # Sets the executed flag of the order.
        self._executed = True

    def fill_order(self, size: float) -> None:
        assert self._executed

        with self._semaphore:
            filled_position = self.market.open_position(self.price, size, self.transact_cost_engine)
            self.assimilate_filled(filled_position)

            if not (self.parent_portfolio is None): # Send updates to the parent.
                self.parent_portfolio.assimilate(filled_position.portfolio)

            self.size -= size

    def cancel_order(self) -> None:
        if not self._executed: # No corrective action necessary for un-executed orders.
            return

        with self._semaphore:
            self.size = 0
            self.filled_position.assimilate(self.market.make_cost_position(self.cancellation_cost))

if __name__ == "__main__":
    pass