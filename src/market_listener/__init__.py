import time

class OrderBook:
    def __init__(self) -> None:
        self.bid_prices = [] # Descending order
        self.bid_sizes  = []
        self.accum_bid_sizes = []
        self.ask_prices = [] # Ascending order
        self.ask_sizes  = []
        self.accum_ask_sizes = []
        self.timestamp = time.time()

    def append_bid(self, bid_price: float, bid_size: float, accum_bid_size: float = None) -> None:
        # Maintains descending order of bid orderbook
        if not self.bid_prices:
            accum_bid_size = bid_size
        else: # Non-empty orderbook
            assert bid_price < self.bid_prices[-1]

        self.bid_prices.append(bid_price)
        self.bid_sizes.append(bid_size)
        self.accum_bid_sizes.append(accum_bid_size if accum_bid_size else \
                self.accum_bid_sizes[-1] + bid_size)

    def append_ask(self, ask_price: float, ask_size: float, accum_ask_size: float = None) -> None:
        # Maintains ascending order of ask orderbook
        if not self.ask_prices:
            accum_ask_size = ask_size
        else: # Non-empty orderbook
            assert ask_price > self.ask_prices[-1]
        
        self.ask_prices.append(ask_price)
        self.ask_sizes.append(ask_size)
        self.accum_ask_sizes.append(accum_ask_size if accum_ask_size else \
                self.accum_ask_sizes[-1] + ask_size)

    def get_bid(self, entry: int = 0) -> tuple[float, float, float]:
        # Returns the <entry>th bid as (price, size, accumulative_size)
        return self.bid_prices[entry], self.bid_sizes[entry], self.accum_bid_sizes[entry]

    def get_ask(self, entry: int = 0) -> tuple[float, float, float]:
        # Returns the <entry>th ask as (price, size, accumulative_size)
        return self.ask_prices[entry], self.ask_sizes[entry], self.accum_ask_sizes[entry]

    def reset(self) -> None:
        self.bid_prices.clear()
        self.bid_sizes.clear()
        self.accum_bid_sizes.clear()
        self.ask_prices.clear()
        self.ask_sizes.clear()
        self.accum_ask_sizes.clear()
        self.timestamp = time.time()

    def empty(self) -> bool:
        return (len(self.bid_prices) == 0) and (len(self.ask_prices) == 0)

class MarketListenerBase:
    def __init__(self, market: tuple[str, str], max_orderbook_entries: int = 10):
        self.market = market
        self.name = self.get_name()
        self.orderbook = OrderBook()
        self.max_orderbook_entries = max_orderbook_entries
    
    def subscribe(self) -> None:
        pass

    def rendered(self) -> bool:
        return True

    def get_name(self) -> str:
        raise NotImplementedError()

    def get_current_price(self) -> float:
        raise NotImplementedError()

    def get_current_bid(self) -> tuple[float, float]:
        # Returns (price, size) for the highest bid
        raise NotImplementedError()

    def get_current_ask(self) -> tuple[float, float]:
        # Returns (price, size) for the lowest ask
        raise NotImplementedError()
    
    def update_orderbook(self) -> None:
        raise NotImplementedError()

    def get_orderbook(self) -> OrderBook:
        # Returns the orderbook (bids, asks)
        if self.orderbook.empty():
            self.update_orderbook()

        return self.orderbook

    def close(self) -> None:
        pass

class MarketListenerStub (MarketListenerBase):
    def get_name(self) -> str:
        return "TestingStub"

    def update_orderbook(self) -> None:
        pass

if __name__ == "__main__":
    pass