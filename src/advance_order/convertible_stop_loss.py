from .stop_loss import StopLoss, StopLossLogic
from .trailing_stop_loss import TrailingStopLoss
from ..market import PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class ConvertibleStopLoss (StopLoss, TrailingStopLoss):
    # Converts from hard stop loss to trailing stop loss
    def __init__(self, position: PositionBase, market_actor: MarketActorBase, market_listener:
        MarketListenerBase, stop_loss: float, trailing_rate: float, use_orderbook: bool = False) -> None:

        StopLoss.__init__(self, position, market_actor, market_listener, stop_loss, use_orderbook)
        TrailingStopLoss.__init__(self, position, market_actor, market_listener,
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

class ConvertibleStopLossLogic (StopLossLogic):
    # Supports only stop_loss as rate
    def __init__(self, market_actor: MarketActorBase, market_listener: MarketListenerBase,
        stop_loss_offset: float, trailing_rate: float = None, offset_as_rate: float = False,
        use_orderbook: bool = False) -> None:
        StopLossLogic.__init__(self, market_actor, market_listener, stop_loss_offset,
                offset_as_rate=offset_as_rate, use_orderbook=use_orderbook)

        if not trailing_rate:
            assert offset_as_rate
            trailing_rate = stop_loss_offset

        self.trailing_rate = trailing_rate

    def open_advance_order(self, position: PositionBase) -> ConvertibleStopLoss:
        return ConvertibleStopLoss(position, self.market_actor, self.market_listener,
                self.get_stop_loss(position), self.trailing_rate,
                use_orderbook=self.use_orderbook)

if __name__ == "__main__":
    pass