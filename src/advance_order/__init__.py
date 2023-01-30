from ..portfolio import Portfolio
from ..market.cost_engine import CostEngine
from ..order import Order
from ..market import MarketBase
from ..market_listener import MarketListenerBase

class AdvanceOrderBase (Order):
    @classmethod
    def make_advance_order(cls, market: MarketBase, market_actor, *args, price: float = None,
        use_orderbook_price: bool = False, **kwargs) -> "AdvanceOrderBase":
        return cls(
            market, *args,
            price=price,
            transact_cost_engine=market_actor.get_transact_cost_engine(market),
            cancellation_cost=market_actor.get_order_cancellation_cost(market),
            parent_portfolio=market_actor.portfolio,
            use_orderbook_price=use_orderbook_price, **kwargs
        )

    # Order with execution dependent on condition derived from a MarketListener object.
    def __init__(self, market: MarketBase, size: float, price: float = None,
        transact_cost_engine: CostEngine = CostEngine(), cancellation_cost: float = 0,
        parent_portfolio: Portfolio = None, use_orderbook_price: bool = False) -> None:
        """
        @param price (float, opt): The order price. If not specified, sets the flag
                use_market_price=True.
        """
        Order.__init__(self, market, price, size, transact_cost_engine, cancellation_cost,
                parent_portfolio)
        
        self.market_listener: MarketListenerBase = market.get_market_listener()
        self.use_orderbook_price = use_orderbook_price
        self._activated = False
        self._use_market_price = (not price)

    @property
    def activated(self) -> bool:
        return self._activated

    def triggers_at_price(self, price: float) -> bool:
        # Returns whether the advance order triggers at the given price.
        raise NotImplementedError()

    def get_current_price(self) -> float:
        if not self.use_orderbook_price:
            return self.market_listener.get_current_price()
        
        return self.market_listener.get_market_ask_price(self.size) if self.short else \
                self.market_listener.get_market_bid_price(self.size)

    def activate_order(self) -> None:
        self._activated = True

    def execute_order(self) -> None:
        if self._use_market_price:
            self.price = self.get_current_price()
            self._use_market_price = False

        Order.execute_order(self)

    def has_triggered(self) -> bool:
        # Predicate function that (performs any updates and) returns whether the AdvanceOrder
        # has been triggered and due for execution.
        return self.triggers_at_price(self.get_current_price())

    def cancel_order(self) -> None:
        self._activated = False
        Order.cancel_order(self)

if __name__ == "__main__":
    pass