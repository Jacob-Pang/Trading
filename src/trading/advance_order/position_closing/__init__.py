from ...portfolio import Portfolio
from ...market import MarketBase, MarketPosition
from ...market.cost_engine import CostEngine
from ...market_actor import MarketActorBase
from ...market_listener import MarketListenerBase
from ...advance_order import AdvanceOrderBase

class PositionClosingAdvanceOrderBase (AdvanceOrderBase):
    @classmethod
    def make_advance_order(cls, market: MarketBase, market_actor: MarketActorBase,
        position: MarketPosition, *args, price: float = None, use_orderbook_price: bool = False,
        auto_assimilate: bool = True, **kwargs) -> "PositionClosingAdvanceOrderBase":

        return cls(
            market, position, *args,
            price=price,
            transact_cost_engine=market_actor.get_transact_cost_engine(market),
            cancellation_cost=market_actor.get_order_cancellation_cost(market),
            parent_portfolio=market_actor.portfolio,
            use_orderbook_price=use_orderbook_price,
            auto_assimilate=auto_assimilate, **kwargs
        )

    # AdvanceOrder that closes an existing position upon trigger and execution event.
    def __init__(self, market: MarketBase, position: MarketPosition, price: float = None,
        transact_cost_engine: CostEngine = CostEngine(), cancellation_cost: float = 0,
        parent_portfolio: Portfolio = None, use_orderbook_price: bool = False,
        auto_assimilate: bool = True) -> None:

        AdvanceOrderBase.__init__(self, market, position.get_closing_size(transact_cost_engine),
                price=price, transact_cost_engine=transact_cost_engine,
                cancellation_cost=cancellation_cost, parent_portfolio=parent_portfolio,
                use_orderbook_price=use_orderbook_price)

        self.closing_position = position
        self.auto_assimilate = auto_assimilate

    def assimilate_filled(self, filled_position: MarketPosition) -> None:
        AdvanceOrderBase.assimilate_filled(self, filled_position)

        if self.auto_assimilate:
            self.closing_position.assimilate(filled_position)

if __name__ == "__main__":
    pass