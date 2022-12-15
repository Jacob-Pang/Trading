from threading import Semaphore
from ..balances import Portfolio
from . import MarketBase
from .cost_engine import CostEngine

class Order:
    def __init__(self, market: MarketBase, price: float, size: float, transact_cost_engine: CostEngine,
        cancellation_cost: float = 0, parent_portfolio: Portfolio = None) -> None:

        self.market = market
        self.price = price
        self.size = size
        self.transact_cost_engine = transact_cost_engine
        self.cancellation_cost = cancellation_cost
        self.parent_portfolio = parent_portfolio
        self.filled_position = market.make_empty_position()
        self._semaphore = Semaphore(1)

    @property
    def filled(self) -> bool:
        return self.size == 0

    def has_filled(self) -> bool:
        # Predicate for property filled
        return self.filled

    def fill_order(self, size: float) -> None:
        with self._semaphore:
            filled_position = self.market.open_position(self.price, size, self.transact_cost_engine)
            self.filled_position.assimilate(filled_position)

            if self.parent_portfolio: # Send updates to the parent.
                self.parent_portfolio.assimilate(filled_position.balances)

            self.size -= size

    def cancel_order(self) -> None:
        with self._semaphore:
            self.size = 0
            self.filled_position.assimilate(self.market.make_cost_position(self.cancellation_cost))

if __name__ == "__main__":
    pass