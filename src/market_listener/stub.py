from . import MarketListenerBase

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