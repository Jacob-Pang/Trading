from . import AdvanceOrderBase
from .advance_order_logic import AdvanceOrderLogicBase
from ..market import PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class TrailingStopLoss (AdvanceOrderBase):
    def __init__(self, position: PositionBase, market_actor: MarketActorBase, market_listener:
        MarketListenerBase, trailing_rate: float, use_orderbook: bool = False) -> None:
        AdvanceOrderBase.__init__(self, position, market_actor, market_listener, use_orderbook)

        self.entry_price = self.position.avg_price
        self.benchmark_price = self.position.avg_price
        self.trailing_rate = trailing_rate
        self.stop_loss_price = self.get_stop_loss(self.entry_price)

    def get_stop_loss(self, price: float) -> float:
        # Returns the stop loss at the given price.
        return (1 + self.trailing_rate) * price if self.position.short else \
                (1 - self.trailing_rate) * price

    def trigger(self, price: float) -> bool:
        if self.position.short:
            if price < self.benchmark_price:
                self.stop_loss_price = self.get_stop_loss(price)
                self.benchmark_price = price

            return price >= self.stop_loss_price
        
        if price > self.benchmark_price:
            self.stop_loss_price = self.get_stop_loss(price)
            self.benchmark_price = price

        return price <= self.stop_loss_price

class TrailingStopLossLogic (AdvanceOrderLogicBase):
    def __init__(self,  market_actor: MarketActorBase, market_listener: MarketListenerBase,
        trailing_rate: float, use_orderbook: bool = False) -> None:
        AdvanceOrderLogicBase.__init__(self, market_actor, market_listener,
                use_orderbook=use_orderbook)

        self.traling_rate = trailing_rate

    def open_advance_order(self, position: PositionBase) -> AdvanceOrderBase:
        return TrailingStopLoss(position, self.market_actor, self.market_listener,
                self.traling_rate, use_orderbook=self.use_orderbook)

if __name__ == "__main__":
    pass