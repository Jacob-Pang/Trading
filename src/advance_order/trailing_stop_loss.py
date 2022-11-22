from . import AdvanceOrderBase
from ..market import PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class TrailingStopLoss (AdvanceOrderBase):
    def __init__(self, position: PositionBase, market_actor: MarketActorBase,
        market_listener: MarketListenerBase, entry_price: float, trailing_rate: float,
        use_orderbook: bool = False) -> None:
        AdvanceOrderBase.__init__(self, position, market_actor, market_listener, use_orderbook)

        self.entry_price = entry_price
        self.benchmark_price = entry_price
        self.trailing_rate = trailing_rate
        self.stop_loss_price = self.get_stop_loss(entry_price)

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

if __name__ == "__main__":
    pass