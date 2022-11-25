from . import AdvanceOrderBase
from .advance_order_logic import AdvanceOrderLogicBase
from ..market import PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class StopLoss (AdvanceOrderBase):
    def __init__(self, position: PositionBase, market_actor: MarketActorBase,
        market_listener: MarketListenerBase, stop_loss: float, use_orderbook: bool = False) -> None:

        AdvanceOrderBase.__init__(self, position, market_actor, market_listener, use_orderbook)    
        self.stop_loss_price = stop_loss

    def trigger(self, price: float) -> bool:
        if self.position.short:
            return price >= self.stop_loss_price

        return price <= self.stop_loss_price

class StopLossLogic (AdvanceOrderLogicBase):
    def __init__(self,  market_actor: MarketActorBase, market_listener: MarketListenerBase,
        stop_loss_offset: float, offset_as_rate: bool = False, use_orderbook: bool = False) -> None:
        AdvanceOrderLogicBase.__init__(self, market_actor, market_listener,
                use_orderbook=use_orderbook)

        self.stop_loss_offset = stop_loss_offset
        self.offset_as_rate = offset_as_rate

    def get_stop_loss(self, position: PositionBase) -> float:
        entry_price = position.avg_price

        if self.offset_as_rate:
            return (1 + self.stop_loss_offset) * entry_price if position.short else \
                    (1 - self.stop_loss_offset) * entry_price
        
        return (entry_price + self.stop_loss_offset) if position.short else \
                (entry_price - self.stop_loss_offset)

    def open_advance_order(self, position: PositionBase) -> AdvanceOrderBase:
        return StopLoss(position, self.market_actor, self.market_listener,
                self.get_stop_loss(position), use_orderbook=self.use_orderbook)

if __name__ == "__main__":
    pass