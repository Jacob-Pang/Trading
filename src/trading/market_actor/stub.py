import time

from . import MarketActorBase
from ..order import Order
from ..portfolio import Portfolio
from ..market import MarketBase
from ..market.cost_engine import CostEngine

class MarketActorStub (MarketActorBase):
    # For training and testing purposes
    def __init__(self, transact_flat_cost: float = 0, transact_min_cost: float = 0,
        transact_var_cost_rate_percent: float = 0, portfolio: Portfolio = None,
        order_update_freq: float = .2, name: str = "market_actor_stub", echo_mode: bool = True) -> None:
        """
        @param transact_var_cost_rate_percent (float): The variable transaction cost rate in percentage terms.
        """
        MarketActorBase.__init__(self, portfolio, order_update_freq)
        self.transact_flat_cost = transact_flat_cost
        self.transact_min_cost = transact_min_cost
        self.transact_var_cost_rate = transact_var_cost_rate_percent / 100
        self.name = name
        self.echo_mode = echo_mode
        
    def get_name(self) -> str:
        return self.name

    def get_transact_cost_engine(self, market: MarketBase) -> float:
        return CostEngine(self.transact_flat_cost, self.transact_min_cost, self.transact_var_cost_rate)

    def _submit_order(self, order: Order) -> None:
        if not self.echo_mode: return
        if order.size > 0: # Long position
            print(f"Submitted buy order of {order.size:.2f} {order.market.base_ticker:<10}",
                    f"at {order.price:.2f}")
        else:
            print(f"Submitted sell order of {abs(order.size):.2f} {order.market.base_ticker:<10}",
                    f"at {order.price:.2f}")

    def _update_order(self, order: Order) -> float:
        fill_size = order.size
        if not self.echo_mode: return fill_size
        
        if fill_size > 0: # Long position
            print(f"Filled buy order of {fill_size:.2f} {order.market.base_ticker:<10}",
                    f"at {order.price:.2f}")
        else:
            print(f"Filled sell order of {abs(order.size):.2f} {order.market.base_ticker:<10}",
                    f"at {order.price:.2f}")

        return fill_size

if __name__ == "__main__":
    pass