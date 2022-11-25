from ..market import MarketBase
from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase

class TradingSizeLogicInterface:
    def get_open_long_size(self) -> float:
        # Returns the size to open for a long position.
        raise NotImplementedError()
    
    def get_open_short_size(self) -> float:
        # Returns the size to open for a short position.
        raise NotImplementedError()

class TradingSizeLogicBase (TradingSizeLogicInterface):
    def __init__(self, market_actor: MarketActorBase, market_listener: MarketListenerBase):
        self.market_actor = market_actor
        self.market_listener = market_listener

    @property
    def market(self) -> MarketBase:
        return self.market_listener.market

    def get_open_long_size(self) -> float:
        # Transacts against ask prices
        ask_price, ask_size = self.market_listener.get_current_ask()
        
        return 1

    def get_open_short_size(self) -> float:
        # Transacts against bid prices
        bid_price, bid_size = self.market_listener.get_current_bid()
        
        return 1

if __name__ == "__main__":
    pass