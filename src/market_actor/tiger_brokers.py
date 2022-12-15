from tigeropen.common.util.order_utils import market_order
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.trade.trade_client import TradeClient
from tigeropen.tiger_open_config import get_client_config

from . import MarketActorBase
from ..market import MarketBase, PositionBase
from ..market.spot import Spot
from ..market.derivative import Derivative
from ..balances import Portfolio

class TigerBrokersTaker (MarketActorBase):
    def __init__(self, prviate_key_path: str, user_id: int, account: int, portfolio: Portfolio = Portfolio(),
        max_leverage: float = 1.):
        MarketActorBase.__init__(self, portfolio, max_leverage)
        self.client_config = get_client_config(private_key_path=prviate_key_path, tiger_id=user_id,
                account=account)
        
        self.trade_client = TradeClient(self.client_config)

    def get_name(self) -> str:
        return "tiger_brokers_taker"

    def get_transact_cost_fn(self, market: MarketBase) -> float:
        # Returns the transaction fee rate for the given market
        pass

    def place_order(self, market: MarketBase, price: float, size: float) -> tuple[float, float]:
        # Places an order on the market and returns the filled_size and average filled price.
        # Negative sizes indicate opening of short positions.
        raise NotImplementedError()

if __name__ == "__main__":
    pass