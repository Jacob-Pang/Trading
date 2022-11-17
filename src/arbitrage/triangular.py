from . import LongArbitrageNode, ShortArbitrageNode
from . import pass_through_path, execute_trades
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase
from ..trading_logic import TradingLogicBase

class TriangularArbitrage:
    def __init__(self, origin_curr: str, trading_logic: TradingLogicBase, market_listeners:
        list[MarketListenerBase], market_actors: list[MarketActorBase]):
        """ Params:
        origin_curr (str): The currency to set as the origin and destination of the
                triangular arbitrage. Note that any gains will be denominated in this currency.
        market_listeners (list[MarketListenerBase]): The 3 distinct market_listeners to set up
                the triangle (e.g. XXX/ORG, XXX/YYY, YYY/ORG)
        market_actors (list[MarketActorBase]): The market actors to use to execute orders
                corresponding to each listener.
        """
        self.origin_curr = origin_curr
        
        market_mapping = {
            market_listener.market: (market_listener, market_actor)
            for market_listener, market_actor in zip(market_listeners, market_actors)
        }

        source_curr = origin_curr
        self.forward_path = []
        self.reverse_path = []

        while (not self.forward_path or source_curr != origin_curr) and market_mapping:
            market = None

            for _market in market_mapping:
                if source_curr in _market:
                    market = _market
                    break
            
            assert market # Path exists
            market_listener, market_actor = market_mapping.pop(market)
            base, quote = market

            if quote == source_curr:
                source_curr = base
                self.forward_path.append(LongArbitrageNode(trading_logic, market_listener, market_actor))
                self.reverse_path.append(ShortArbitrageNode(trading_logic, market_listener, market_actor))
            else:
                source_curr = quote
                self.forward_path.append(ShortArbitrageNode(trading_logic, market_listener, market_actor))
                self.reverse_path.append(LongArbitrageNode(trading_logic, market_listener, market_actor))

        self.reverse_path = list(reversed(self.reverse_path))

    def scan_and_execute(self, origin_size: float) -> bool:
        # Returns whether any trades were executed
        forward_value, forward_origin_size = pass_through_path(self.forward_path, origin_size)

        if forward_value > 1: # Arbitrage opportunity
            execute_trades(self.forward_path, forward_origin_size)
            return True # Does not check reverse

        reverse_value, reverse_origin_size = pass_through_path(self.reverse_path, origin_size)

        if reverse_value > 1: # Arbitrage opportunity
            execute_trades(self.reverse_path, reverse_origin_size)
            return True
        
        return False

if __name__ == "__main__":
    pass
