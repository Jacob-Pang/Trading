from . import AdvanceOrderBase
from ..market import PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class AdvanceOrderLogicInterface:
    # Function signature for opening advance_orders
    # Not a requirement to use MarketActors or MarketListeners.
    def open_advance_order(self, position: PositionBase) -> AdvanceOrderBase:
        raise NotImplementedError()

class AdvanceOrderLogicBase (AdvanceOrderLogicInterface):
    # Default skeleton for advance_order_logic implementations
    def __init__(self,  market_actor: MarketActorBase, market_listener: MarketListenerBase,
        use_orderbook: bool = False) -> None:
        self.market_actor = market_actor
        self.market_listener = market_listener
        self.use_orderbook = use_orderbook

    def open_advance_order(self, position: PositionBase) -> AdvanceOrderBase:
        return AdvanceOrderBase(position, self.market_actor, self.market_listener,
                use_orderbook=self.use_orderbook)

if __name__ == "__main__":
    pass