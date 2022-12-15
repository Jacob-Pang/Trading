from threading import Thread
from ..balances import Portfolio
from ..market import MarketBase, PositionBase
from ..market.cost_engine import CostEngine
from ..market.order import Order

class MarketActorBase:
    def __init__(self, portfolio: Portfolio = Portfolio(), max_leverage: float = 1.):
        self.portfolio = portfolio
        self.max_leverage = max_leverage

    def get_name(self) -> str:
        raise NotImplementedError()

    def get_order_cancellation_cost(self, market: MarketBase) -> float:
        # Returns the order cancellation costs for the given market
        return 0

    def get_transact_cost_engine(self, market: MarketBase) -> CostEngine:
        # Returns the transaction cost engine for the given market
        return CostEngine()

    def manage_order_fills(self, order: Order) -> None:
        raise NotImplementedError()
    
    def place_order(self, order: Order) -> None:
        raise NotImplementedError()

    def place_open_order(self, market: MarketBase, price: float, size: float) -> Order:
        """ Places an order to open a new position.

        @param market (MarketBase): The market to place an order for.
        @param price (float): The price to order at.
        @param size (float): The number of contracts or size of position to order.

        @returns order (Order): The order to open the position:
                order.filled (property): returns whether the order has been filled.
                order.filled_position (property): returns the resulting position (PositionBase).

        Notes: filling of the order automatically updates the MarketActor's portfolio.
        """
        order = Order(market, price, size, transact_cost_engine=self.get_transact_cost_engine(market),
                cancellation_cost=self.get_order_cancellation_cost(market),
                parent_portfolio=self.portfolio)
        
        self.place_order(order)
        Thread(target=self.manage_order_fills, args=(order,)).start()
        return order

    def close_position(self, position: PositionBase, price: float) -> Order:
        # Places an order to close the existing position at the given price.
        contra_size = position.get_closing_size(self.get_transact_cost_engine(position.market))

        return self.place_open_order(position.market, price, contra_size)

if __name__ == "__main__":
    pass