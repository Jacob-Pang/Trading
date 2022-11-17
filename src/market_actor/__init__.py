class MarketActorBase:
    def get_name(self) -> str:
        raise NotImplementedError()

    def get_transact_fee_rate(self, market: tuple[str, str]) -> float:
        raise NotImplementedError()

    def place_buy_order(self, market: tuple[str, str], price: float, size: float) -> None:
        raise NotImplementedError()

    def place_sell_order(self, market: tuple[str, str], price: float, size: float) -> None:
        raise NotImplementedError()

class EchoMarketActor (MarketActorBase):
    def __init__(self, name: str, transact_fee_rate: float) -> None:
        self.name = name
        self.transact_fee_rate = transact_fee_rate

    def get_transact_fee_rate(self, market: tuple[str, str]) -> float:
        return self.transact_fee_rate

    def place_buy_order(self, market: tuple[str, str], price: float, size: float) -> None:
        base, quote = market
        print(f"Buy  {size:.2f} {base:<5} at {price:.2f} {quote:<5}")

    def place_sell_order(self, market: tuple[str, str], price: float, size: float) -> None:
        base, quote = market
        print(f"Sell {size:.2f} {base:<5} at {price:.2f} {quote:<5}")

if __name__ == "__main__":
    pass