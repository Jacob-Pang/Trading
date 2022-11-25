from ..market import MarketBase, PositionBase
from ..balances import Portfolio

class MarketActorBase:
    def __init__(self, portfolio: Portfolio = Portfolio()):
        self.portfolio = portfolio

    def get_name(self) -> str:
        raise NotImplementedError()

    def get_transact_fee_rate(self, market: MarketBase) -> float:
        # Returns the transaction fee rate for the given market
        raise NotImplementedError()

    def place_order(self, market: MarketBase, price: float, size: float) -> float:
        # Places an order on the market and returns the average filled price.
        # Negative sizes indicate opening of short positions.
        raise NotImplementedError()

    def open_position(self, market: MarketBase, price: float, size: float,
        as_contra_position: bool = False) -> PositionBase:

        transact_fee_rate = self.get_transact_fee_rate(market)
        order_size = market.get_contra_position_size(size, transact_fee_rate) if as_contra_position else size
        avg_filled_price = self.place_order(market, price, order_size)
        
        # Estimates and may possibly vary from realized positions
        position = market.open_position(avg_filled_price, size, transact_fee_rate, as_contra_position)
        self.portfolio.assimilate(position.balances) # Record the changes in balances

        return position

class MarketActorStub (MarketActorBase):
    # For training and testing purposes
    def __init__(self, transact_fee_rate: float, portfolio: Portfolio = Portfolio(),
        name: str = "market_actor_stub", echo_mode: bool = True):
        super().__init__(portfolio)

        self.transact_fee_rate = transact_fee_rate
        self.name = name
        self.echo_mode = echo_mode
        
    def get_name(self) -> str:
        return self.name

    def get_transact_fee_rate(self, market: MarketBase) -> float:
        return self.transact_fee_rate

    def place_order(self, market: MarketBase, price: float, size: float) -> float:
        if self.echo_mode:
            if size > 0: # Long position
                print(f"Bought {size:.2f} units of {market.get_ticker():<10} at {price:.2f}")
            else:
                print(f"Sold   {abs(size):.2f} units of {market.get_ticker():<10} at {price:.2f}")

        return price

if __name__ == "__main__":
    pass