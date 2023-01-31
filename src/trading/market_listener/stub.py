from . import MarketListenerBase

class MarketListenerStub (MarketListenerBase):
    current_price: float = None

    # Setter
    def set_current_price(self, price: float) -> None:
        self.current_price = price

    def get_current_price(self) -> float:
        return self.current_price

    def update_orderbook(self) -> None:
        pass

    def update_tradebook(self) -> None:
        pass

if __name__ == "__main__":
    pass