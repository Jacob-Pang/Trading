from ..market_actor import MarketActorBase
from ..market_listener import MarketListenerBase
from ..trading_logic import TradingLogicBase

class ArbitrageNodeBase:
    def __init__(self, trading_logic: TradingLogicBase, market_listener: MarketListenerBase,
        market_actor: MarketActorBase):
        self.trading_logic = trading_logic
        self.market_listener = market_listener
        self.market_actor = market_actor
        
        # caching optimizations
        self.timestamp =  None
        self._trade_price = None
        self._trade_size_factor = None

    @property
    def synced(self) -> bool:
        return self.timestamp == self.market_listener.orderbook.timestamp

    def get_transact_fee_rate(self) -> float:
        return self.market_actor.get_transact_fee_rate(self.market_listener.market)

    def get_trade_price(self) -> float:
        # Returns the price to trade at based on trading_logic
        raise NotImplementedError()
    
    def get_tradeable_size(self) -> float:
        # Returns the maximum size tradeable based on trading_logic
        raise NotImplementedError()

    def get_trade_size_factor(self, price: float) -> float:
        # Returns the size to trade for one unit of source currency at the price.
        raise NotImplementedError()

    def pass_through(self, pass_through_value: float, origin_size: float, source_size:
        float) -> tuple[float, float, float]:

        self._trade_price = self.get_trade_price()
        self._trade_size_factor = self.get_trade_size_factor(self._trade_price)
        tradeable_size = self.get_tradeable_size()

        # sync timestamps
        self.timestamp = self.market_listener.orderbook.timestamp
        dest_size = source_size * self._trade_size_factor

        if dest_size > tradeable_size:
            # size constraints
            origin_size *= (tradeable_size / dest_size)
            dest_size = tradeable_size
        
        # transact cost reductions
        pass_through_value *= (1. - self.get_transact_fee_rate()) * self._trade_size_factor
        dest_size *= (1. - self.get_transact_fee_rate())

        return pass_through_value, origin_size, dest_size

    def place_order(self, price: float, size: float) -> None:
        raise NotImplementedError()

    def execute_trade(self, source_size: float) -> float:
        # executes the order through the market actor and returns the ending size in base currency
        if not self.synced:
            self._trade_price = self.get_trade_price()
            self._trade_size_factor = self.get_trade_size_factor(self._trade_price)

        dest_size = source_size * self._trade_size_factor
        self.place_order(self._trade_price, dest_size)

        # transact cost reductions
        return dest_size * (1. - self.get_transact_fee_rate())

    def __str__(self) -> str:
        raise NotImplementedError()

class LongArbitrageNode (ArbitrageNodeBase):
    def get_trade_price(self) -> float:
        return self.trading_logic.get_buy_price_from_orderbook(self.market_listener.get_orderbook())

    def get_tradeable_size(self) -> float:
        return self.trading_logic.get_buy_size_from_orderbook(self.market_listener.get_orderbook())

    def get_trade_size_factor(self, price: float) -> float:
        return 1 / price

    def place_order(self, price: float, size: float) -> float:
        self.market_actor.place_buy_order(self.market_listener.market, price, size)

    def __str__(self) -> str:
        return f"Long {self.market_listener.market}"

class ShortArbitrageNode (ArbitrageNodeBase):
    def get_trade_price(self) -> float:
        return self.trading_logic.get_sell_price_from_orderbook(self.market_listener.get_orderbook())

    def get_tradeable_size(self) -> float:
        return self.trading_logic.get_sell_size_from_orderbook(self.market_listener.get_orderbook())

    def get_trade_size_factor(self, price: float) -> float:
        return price

    def place_order(self, price: float, size: float) -> float:
        self.market_actor.place_sell_order(self.market_listener.market, price, size)

    def __str__(self) -> str:
        return f"Short {self.market_listener.market}"

def pass_through_path(path: list[ArbitrageNodeBase], origin_size: float) -> tuple[float, float]:
    # Returns the pass_through_value for one unit of origin_currency and tradeable origin_size.
    pass_through_value = 1.
    source_size = origin_size

    for node in path:
        pass_through_value, origin_size, source_size = node.pass_through(pass_through_value,
                origin_size, source_size)

    return pass_through_value, origin_size

def execute_trades(path: list[ArbitrageNodeBase], origin_size: float) -> float:
    # Returns the ending size in origin_currency
    dest_size = origin_size

    for node in path:
        dest_size = node.execute_trade(dest_size)

    return dest_size

if __name__ == "__main__":
    pass
