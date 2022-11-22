from . import MarketBase, PositionBase
from ..balances import Balances

class DerivativePosition (PositionBase):
    def __init__(self, market: "Derivative", entry_price: float, balances: Balances) -> None:
        super().__init__(market, entry_price, balances)

    def get_open_size(self) -> float:
        # Returns the opened size of the position
        return self.balances.get(self.market.ticker)

class Derivative (MarketBase):
    def __init__(self, ticker: str, funding_currency: str) -> None:
        self.ticker = ticker
        self.funding_currency = funding_currency
        
        MarketBase.__init__(self)

    def get_ticker(self) -> str:
        return self.ticker

    def open_position(self, entry_price: float, size: float, transact_fee_rate: float,
        as_contra_position: bool = False) -> PositionBase:
        end_balances = Balances()

        if as_contra_position:
            size = self.get_contra_position_size(size, transact_fee_rate)

        end_balances.add(self.ticker, size)
        end_balances.add(self.funding_currency, -transact_fee_rate * entry_price * size)

        return DerivativePosition(self, entry_price, end_balances)

if __name__ == "__main__":
    pass