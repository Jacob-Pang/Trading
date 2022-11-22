from .stop_loss import StopLoss
from .trailing_stop_loss import TrailingStopLoss
from ..market import PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class ConvertibleStopLoss (StopLoss, TrailingStopLoss):
    # Converts from hard stop loss to trailing stop loss
    def __init__(self, position: PositionBase, market_actor: MarketActorBase,
        market_listener: MarketListenerBase, entry_price: float, stop_loss: float,
        trailing_rate: float, stop_loss_as_rate: bool = False, use_orderbook: bool = False) -> None:

        StopLoss.__init__(self, position, market_actor, market_listener, stop_loss, entry_price,
                stop_loss_as_rate, use_orderbook)

        TrailingStopLoss.__init__(self, position, market_actor, market_listener, entry_price,
                trailing_rate, use_orderbook)

    def get_stop_loss(self, price: float) -> float:
        trailing_stop_loss = TrailingStopLoss.get_stop_loss(self, price)

        if self.position.short:
            if trailing_stop_loss < self.entry_price:
                # Convert to trailing
                return trailing_stop_loss
        elif trailing_stop_loss > self.entry_price:
            # Convert to trailing
            return trailing_stop_loss

        return self.stop_loss_price

    def trigger(self, price: float) -> bool:
        return TrailingStopLoss.trigger(self, price)

if __name__ == "__main__":
    pass