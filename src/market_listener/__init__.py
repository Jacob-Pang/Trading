from ..listener import ListenerBase
from ..orderbook import Orderbook
from ..tradebook import Tradebook

class MarketListenerBase (ListenerBase):
    def __init__(self, tradebook_capacity: int = 100, max_orderbook_entries: int = None):
        self.orderbook = Orderbook()
        self.tradebook = Tradebook(tradebook_capacity)
        self.max_orderbook_entries = max_orderbook_entries

    # Getters
    def get(self) -> float:
        return self.get_current_price()

    def get_current_price(self) -> float:
        raise NotImplementedError()

    def get_current_bid(self) -> tuple[float, float]:
        # Returns (bid_price, bid_size) for the highest bid
        with self._update_semaphore:
            return self.orderbook.get_current_bid()

    def get_current_ask(self) -> tuple[float, float]:
        # Returns (ask_price, ask_size) for the lowest ask
        with self._update_semaphore:
            return self.orderbook.get_current_ask()

    def get_market_bid_price(self, size: float) -> float:
        with self._update_semaphore:
            return self.orderbook.get_market_bid_price(size)

    def get_market_ask_price(self, size: float) -> float:
        with self._update_semaphore:
            return self.orderbook.get_market_ask_price(size)

    def get_orderbook(self) -> Orderbook:
        return self.orderbook

    def get_tradebook(self) -> Tradebook:
        return self.tradebook

    # Mutators
    def update(self) -> None:
        # Updates both orderbook and tradebook
        with self._update_semaphore:
            self.update_orderbook()
            self.update_tradebook()

    def update_orderbook(self) -> None:
        # Update the orderbook up to <self.max_orderbook_entries>.
        raise NotImplementedError()

    def update_tradebook(self) -> None:
        raise NotImplementedError()

if __name__ == "__main__":
    pass