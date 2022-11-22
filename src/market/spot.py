from . import MarketBase, PositionBase
from ..balances import Balances

class SpotPosition (PositionBase):
    def __init__(self, market: "Spot", entry_price: float, balances: Balances) -> None:
        super().__init__(market, entry_price, balances)

    def get_open_size(self) -> float:
        # Returns the opened size of the position
        return self.balances.get(self.market.base)

class Spot (MarketBase):
    def __init__(self, base: str, quote: str) -> None:
        self.base = base
        self.quote = quote

        MarketBase.__init__(self)
    
    def get_ticker(self) -> str:
        return f"{self.base}/{self.quote}"

    def get_contra_position_size(self, size: float, transact_fee_rate: float) -> float:
        if size < 0: # Adjustment only for short positions
            return - size / (1. - transact_fee_rate)

        return - size

    def open_position(self, entry_price: float, size: float, transact_fee_rate: float,
        as_contra_position: bool = False) -> PositionBase:
        end_balances = Balances()

        if as_contra_position:
            # Open a contra-position to size instead
            contra_position = self.get_contra_position_size(size, transact_fee_rate)

            if contra_position > 0: # Long contra_position to short existing_position
                end_balances.add(self.base, abs(size)) # Invert from negative to positive
                end_balances.add(self.quote, -(entry_price * contra_position))
            else: # Short contra_position to long existing_position
                end_balances.add(self.base, contra_position)
                end_balances.add(self.quote, -(1. - transact_fee_rate) * (entry_price * contra_position))
        elif size > 0: # Long position: transaction fee incurred against base currency
            end_balances.add(self.base, (1. - transact_fee_rate) * size)
            end_balances.add(self.quote, -(entry_price * size))
        else: # Short position: transaction fee incurred against quote currency
            end_balances.add(self.base, size)
            end_balances.add(self.quote, -(1. - transact_fee_rate) * (entry_price * size))

        return SpotPosition(self, entry_price, end_balances)

if __name__ == "__main__":
    pass