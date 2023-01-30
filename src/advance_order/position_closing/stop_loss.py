from . import PositionClosingAdvanceOrderBase
from ...portfolio import Portfolio
from ...market import MarketBase, MarketPosition
from ...market.cost_engine import CostEngine
from ...market_actor import MarketActorBase
from ...market_listener import MarketListenerBase

class StopLoss (PositionClosingAdvanceOrderBase):
    @classmethod
    def make_advance_order(cls, market: MarketBase, market_actor: MarketActorBase,
        position: MarketPosition, stop_loss_price: float, *args, price: float = None,
        use_orderbook_price: bool = False, auto_assimilate: bool = True, **kwargs) -> "StopLoss":

        return cls(
            market, position, stop_loss_price, *args,
            price=price,
            transact_cost_engine=market_actor.get_transact_cost_engine(market),
            cancellation_cost=market_actor.get_order_cancellation_cost(market),
            parent_portfolio=market_actor.portfolio,
            use_orderbook_price=use_orderbook_price,
            auto_assimilate=auto_assimilate, **kwargs
        )

    def __init__(self, market: MarketBase, position: MarketPosition, stop_loss_price: float,
        price: float = None, transact_cost_engine: CostEngine = CostEngine(),
        cancellation_cost: float = 0, parent_portfolio: Portfolio = None,
        use_orderbook_price: bool = False, auto_assimilate: bool = True) -> None:

        PositionClosingAdvanceOrderBase.__init__(self, market, position, price=price,
                transact_cost_engine=transact_cost_engine, cancellation_cost=cancellation_cost,
                parent_portfolio=parent_portfolio, use_orderbook_price=use_orderbook_price,
                auto_assimilate=auto_assimilate)

        self.stop_loss_price = stop_loss_price

    def triggers_at_price(self, price: float) -> bool:
        return (price <= self.stop_loss_price) if self.short else (price >= self.stop_loss_price)

class TrailingStopLoss (StopLoss):
    @classmethod
    def make_advance_order(cls, market: MarketBase, market_actor: MarketActorBase,
        position: MarketPosition, trailing_gap: float, *args, price: float = None,
        use_orderbook_price: bool = False, auto_assimilate: bool = True,
        **kwargs) -> "TrailingStopLoss":

        return cls(
            market, position, trailing_gap, *args,
            price=price,
            transact_cost_engine=market_actor.get_transact_cost_engine(market),
            cancellation_cost=market_actor.get_order_cancellation_cost(market),
            parent_portfolio=market_actor.portfolio,
            use_orderbook_price=use_orderbook_price,
            auto_assimilate=auto_assimilate, **kwargs
        )
    
    def __init__(self, market: MarketBase, position: MarketPosition, trailing_gap: float,
        price: float = None, transact_cost_engine: CostEngine = CostEngine(),
        cancellation_cost: float = 0, parent_portfolio: Portfolio = None,
        use_orderbook_price: bool = False, auto_assimilate: bool = True) -> None:

        StopLoss.__init__(self, market, position, None, price=price,
                transact_cost_engine=transact_cost_engine, cancellation_cost=cancellation_cost,
                parent_portfolio=parent_portfolio, use_orderbook_price=use_orderbook_price,
                auto_assimilate=auto_assimilate)

        self.trailing_gap = trailing_gap
        self.record_price = self.get_current_price()
        self.update_stop_loss_price(self.record_price)

    def update_record_price(self, price: float) -> float:
        # Updates and returns the record (short: highest, long: lowest) price
        if self.short and price > self.record_price:
            self.record_price = price
        elif not self.short and price < self.record_price:
            self.record_price = price
        
        return self.record_price

    def update_stop_loss_price(self, price: float) -> float:
        # Updates the stop_loss_price
        self.update_record_price(price)
        self.stop_loss_price = (self.record_price - self.trailing_gap) if self.short else \
                (self.record_price + self.trailing_gap)

        return self.stop_loss_price

    def triggers_at_price(self, price: float) -> bool:
        self.update_stop_loss_price(price)
        return StopLoss.triggers_at_price(self, price)

class TrailingPercentStopLoss (TrailingStopLoss):
    @classmethod
    def make_advance_order(cls, market: MarketBase, market_actor: MarketActorBase,
        position: MarketPosition, trailing_gap_percent: float, *args, price: float = None,
        use_orderbook_price: bool = False, auto_assimilate: bool = True, **kwargs) -> "TrailingStopLoss":

        return cls(
            market, position, trailing_gap_percent, *args,
            price=price,
            transact_cost_engine=market_actor.get_transact_cost_engine(market),
            cancellation_cost=market_actor.get_order_cancellation_cost(market),
            parent_portfolio=market_actor.portfolio,
            use_orderbook_price=use_orderbook_price,
            auto_assimilate=auto_assimilate, **kwargs
        )

    def __init__(self, market: MarketBase, position: MarketPosition, trailing_gap_percent: float,
        price: float = None, transact_cost_engine: CostEngine = CostEngine(),
        cancellation_cost: float = 0, parent_portfolio: Portfolio = None,
        auto_assimilate: bool = True, use_orderbook_price: bool = False) -> None:
        """
        @param trailing_gap_percent (float): the trailing gap in percentage terms.
        """
        TrailingStopLoss.__init__(self, market, position, trailing_gap_percent / 100, price=price,
                transact_cost_engine=transact_cost_engine, cancellation_cost=cancellation_cost,
                parent_portfolio=parent_portfolio, use_orderbook_price=use_orderbook_price,
                auto_assimilate=auto_assimilate)

    def update_stop_loss_price(self, price: float) -> float:
        # Updates the stop_loss_price
        self.update_record_price(price)
        self.stop_loss_price = self.record_price * (1 - self.trailing_gap / 100 if self.short else \
                1 + self.trailing_gap / 100)

        return self.stop_loss_price

if __name__ == "__main__":
    pass
