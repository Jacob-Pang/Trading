from ..market import MarketBase, PositionBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase
from pyutils.events import wait_for

class AdvanceOrderBase:
    def __init__(self, position: PositionBase, market_actor: MarketActorBase,
        market_listener: MarketListenerBase, use_orderbook: bool = False) -> None:
        """
        @param use_orderbook (bool, opt = False): Whether to use the orderbook prices
                as the benchmark for the trigger (otherwise uses the current price).
        """
        assert position.market == market_listener.market

        self.position = position
        self.market_actor = market_actor
        self.market_listener = market_listener
        self.use_orderbook = use_orderbook

    @property
    def market(self) -> MarketBase:
        return self.position.market

    @property
    def filled(self) -> None:
        return self.position.closed

    def get_orderbook_price(self) -> float:
        # Returns the best price in the orderbook
        return self.market_listener.get_current_ask()[0] if self.position.short else \
                self.market_listener.get_current_bid()[0]

    def trigger(self, price: float) -> bool:
        # Returns whether the trigger has been activated at the price.
        raise NotImplementedError()

    def update(self) -> None:
        # Updates and trigger where applicable.
        # Can be overriden for more complex filling processes
        if self.filled:
            return

        curr_price = self.get_orderbook_price() if self.use_orderbook else \
                self.market_listener.get_current_price()

        if not self.trigger(curr_price):
            return

        # Close the position
        close_order = self.market_actor.close_position(self.position, curr_price)
        wait_for(close_order.has_filled)
        self.position.assimilate(close_order.filled_position)

if __name__ == "__main__":
    pass