import time

from threading import Thread
from ..order import Order
from ..advance_order import AdvanceOrderBase
from ..portfolio import Portfolio
from ..market import MarketBase, MarketPosition
from ..market.cost_engine import CostEngine

class MarketActorBase:
    def __init__(self, portfolio: Portfolio = None, order_update_freq: float = .2):
        self.portfolio = portfolio if portfolio else Portfolio()
        self.order_update_freq = order_update_freq

    # Getters
    def get_name(self) -> str:
        raise NotImplementedError()

    def get_order_cancellation_cost(self, market: MarketBase) -> float:
        # Returns the order cancellation costs for the given market
        return 0

    def get_transact_cost_engine(self, market: MarketBase) -> CostEngine:
        # Returns the transaction cost engine for the given market
        return CostEngine()

    # Abstract actor methods
    def _submit_order(self, order: Order) -> None:
        # Performs the actual submission of order.
        raise NotImplementedError()

    def _update_order(self, order: Order) -> float:
        """ Updates the status of the order and executes any changes to order params (price, size).

        @return fill_size (float): The size filled in the current update (or the change in
                order.filled size to recognize); overriding methods may choose to proactively
                invoke @method order.fill_order and return zero or void.
        """
        raise NotImplementedError()

    def _manage_order(self, order: Order) -> None:
        # Manage the order filling process.
        while True:
            fill_size = self._update_order(order)

            if fill_size:
                order.fill_order(fill_size)
            
            if order.filled:
                break

            time.sleep(self.order_update_freq)

    def _manage_advance_order(self, advance_order: AdvanceOrderBase) -> None:
        # Manage the advance_order triggering and execution process.
        while advance_order.activated:
            if advance_order.has_triggered(): break
            time.sleep(self.order_update_freq)

        if advance_order.activated:
            self.execute_order(advance_order)

    # Public actor methods
    def make_order(self, market: MarketBase, price: float, size: float) -> Order:
        """ Creates an Order object (not executed).

        @param market (MarketBase): The market to place an order for.
        @param price (float): The price to order at.
        @param size (float): The number of contracts or size of position to order.

        @returns order (Order): The order to open the position:
            order.filled (property): returns whether the order has been filled.
            order.filled_position (property): returns the resulting position (PositionBase).
        """
        return Order(
            market, price, size,
            transact_cost_engine=self.get_transact_cost_engine(market),
            cancellation_cost=self.get_order_cancellation_cost(market),
            parent_portfolio=self.portfolio
        )

    def execute_order(self, order: Order) -> None:
        """ Executes an order: submits and manage the filling of the order.
        @param order (Order): the order to execute.

        notes:
            a. Filling of the order are automatically reflected in the MarketActor's portfolio.
            b. The execution of the order can be cancelled through order.cancel_order()
        """
        order.execute_order()
        self._submit_order(order)
        Thread(target=self._manage_order, args=(order,)).start()

    def activate_advance_order(self, advance_order: AdvanceOrderBase) -> None:
        """ Activates an advance order: upon triggering the advance order, submits and manage
        the filling of the (triggered) order.

        @param advance_order (AdvanceOrderBase): the advance order to activate.

        notes:
            a. Filling of the (triggered) order are automatically reflected in the MarketActor's portfolio.
            b. The activation of the advance_order can be cancelled through advance_order.cancel_order()
            c. The execution of the (triggered) order can be cancelled through advance_order.cancel_order()
        """
        advance_order.activate_order()
        Thread(target=self._manage_advance_order, args=(advance_order,)).start()

    def close_position(self, position: MarketPosition, exit_price: float) -> Order:
        """ Executes an order to close the position at the given price.
        @param position (PositionBase): the position to close.
        @param price (float): the price to close the position at.

        @returns close_order (Order): the executed order to close the position:
            close_order.filled (property): returns whether the order has been filled.
            close_order.filled_position (property): returns the resulting position (PositionBase)
            such that:
                if close_order.filled:
                    position.assimilate(close_order.filled_position)
                    position.closed >> True
        """
        # Places an order to close the existing position at the given price.
        contra_size = position.get_closing_size(self.get_transact_cost_engine(position.market))
        close_order = self.make_order(position.market, exit_price, contra_size)
        self.execute_order(close_order)

        return close_order

if __name__ == "__main__":
    pass