from . import AdvanceOrderBase
from ..market import PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class StopLoss (AdvanceOrderBase):
    def __init__(self, position: PositionBase, market_actor: MarketActorBase,
        market_listener: MarketListenerBase, stop_loss: float, entry_price: float = None,
        stop_loss_as_rate: bool = False, use_orderbook: bool = False) -> None:
        AdvanceOrderBase.__init__(self, position, market_actor, market_listener, use_orderbook)

        if stop_loss_as_rate: # <entry_price> must be provided.
            self.stop_loss_price = (1 + stop_loss) * entry_price if self.position.short else \
                    (1 - stop_loss) * entry_price
        else:
            self.stop_loss_price = stop_loss

    def trigger(self, price: float) -> bool:
        if self.position.short:
            return price >= self.stop_loss_price

        return price <= self.stop_loss_price

if __name__ == "__main__":
    pass