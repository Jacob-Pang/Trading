from ..orderbook import Orderbook
from ..tradebook import Tradebook
from ..market import MarketBase

class MarketListenerBase:
    def __init__(self, market: MarketBase, tradebook_capacity: int = 100):
        self.market = market
        self.name = self.get_name()
        self.orderbook = Orderbook()
        self.tradebook = Tradebook(tradebook_capacity)
    
    # Init methods
    def subscribe(self) -> None:
        # Subscribe to the connection
        pass

    def ready(self) -> bool:
        # Returns whether the connection is ready
        return True

    # Getters
    def get_name(self) -> str:
        raise NotImplementedError()

    def get_current_price(self) -> float:
        raise NotImplementedError()

    def get_current_bid(self) -> tuple[float, float]:
        # Returns (bid_price, bid_size) for the highest bid
        raise NotImplementedError()

    def get_current_ask(self) -> tuple[float, float]:
        # Returns (ask_price, ask_size) for the lowest ask
        raise NotImplementedError()
    
    def get_orderbook(self) -> Orderbook:
        return self.orderbook

    def get_tradebook(self) -> Tradebook:
        return self.tradebook

    # Update methods
    def update(self, max_entries: int = None) -> None:
        # Updates both orderbook and tradebook
        self.update_orderbook(max_entries)
        self.update_tradebook()

    def update_orderbook(self, max_entries: int = None) -> None:
        # Update the orderbook up to <max_entries>.
        raise NotImplementedError()

    def update_tradebook(self) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        # Closes the connection
        pass

class MarketListenerStub (MarketListenerBase):
    curr_price = None

    def get_name(self) -> str:
        return "market_listener_stub"

    def set_current_price(self, price: float) -> None:
        self.curr_price = price

    def get_current_price(self) -> float:
        return self.curr_price

    def update_orderbook(self, max_entries: int = None) -> None:
        pass

    def update_tradebook(self) -> None:
        pass

if __name__ == "__main__":
    pass