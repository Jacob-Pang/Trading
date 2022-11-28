from . import MarketBase, PositionBase
from ..balances import Balances

class DerivativePosition (PositionBase):
    def __init__(self, market: "Derivative", entry_price: float, balances: Balances) -> None:
        super().__init__(market, entry_price, balances)

    def get_open_size(self) -> float:
        # Returns the opened size of the position
        return self.balances.get_size(self.market.ticker)

class Derivative (MarketBase):
    def __init__(self, ticker: str, settlement_ticker: str) -> None:
        self.ticker = ticker
        self.settlement_ticker = settlement_ticker
        
        MarketBase.__init__(self)

    def get_ticker(self) -> str:
        return self.ticker

    def get_settlement_ticker(self) -> str:
        # Returns the ticker for the funding currency for the market.
        raise self.settlement_ticker

    def open_position(self, entry_price: float, size: float, transact_fee_rate: float,
        as_contra_position: bool = False) -> PositionBase:
        end_balances = Balances()

        if as_contra_position:
            size = self.get_contra_position_size(size, transact_fee_rate)

        end_balances.add_cfd_balance(self.ticker, self.settlement_ticker, size, entry_price)
        end_balances.add_balance(self.settlement_ticker, -transact_fee_rate * entry_price * size)

        return DerivativePosition(self, entry_price, end_balances)

if __name__ == "__main__":
    pass