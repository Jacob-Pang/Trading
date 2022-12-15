import time

from . import MarketActorBase
from ..balances import Portfolio
from ..market import MarketBase
from ..market.cost_engine import CostEngine
from ..market.order import Order

class MarketActorStub (MarketActorBase):
    # For training and testing purposes
    def __init__(self, transact_flat_cost: float = 0, transact_min_cost: float = 0, transact_percent_cost_rate:
        float = 0, order_fill_delay: int = 0, portfolio: Portfolio = Portfolio(), max_leverage: float = 1.,
        name: str = "market_actor_stub", echo_mode: bool = True):

        super().__init__(portfolio, max_leverage)
        self.transact_flat_cost = transact_flat_cost
        self.transact_min_cost = transact_min_cost
        self.transact_percent_cost_rate = transact_percent_cost_rate
        self.order_fill_delay = order_fill_delay
        self.name = name
        self.echo_mode = echo_mode
        
    def get_name(self) -> str:
        return self.name

    def get_transact_cost_fn(self, market: MarketBase) -> float:
        return CostEngine(self.transact_flat_cost, self.transact_min_cost,
                self.transact_percent_cost_rate)

    def manage_order_fills(self, order: Order) -> None:
        for _ in range(self.order_fill_delay):
            if not order.size:
                return
            
            time.sleep(.9)

        fill_size = order.size
        order.fill_order(fill_size)
        
        if not self.echo_mode:
            return

        if fill_size > 0: # Long position
            print(f"Filled buy order of {fill_size:.2f} {order.market.get_ticker():<10}",
                    f"at {order.filled_position.avg_price:.2f}")
        else:
            print(f"Filled sell order of {abs(order.size):.2f} {order.market.get_ticker():<10}",
                    f"at {order.filled_position.avg_price:.2f}")

    def place_order(self, order: Order) -> None:
        if not self.echo_mode:
            return

        if order.size > 0: # Long position
            print(f"Submitted buy order of {order.size:.2f} {order.market.get_ticker():<10}",
                    f"at {order.price:.2f}")
        else:
            print(f"Submitted sell order of {abs(order.size):.2f} {order.market.get_ticker():<10}",
                    f"at {order.price:.2f}")

if __name__ == "__main__":
    pass