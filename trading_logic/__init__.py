from ..market_listener import OrderBook

class TradingLogicBase:
    # Interface for deriving trading logic
    def get_size_from_funds(self, funds: float) -> float:
        # Returns the maximum tradeable size based on funds
        raise NotImplementedError()

    # Orderbook basis
    def get_buy_price_from_orderbook(self, orderbook: OrderBook) -> float:
        # Returns the price for a long position based on orderbook
        raise NotImplementedError()

    def get_buy_size_from_orderbook(self, orderbook: OrderBook) -> float:
        # Returns the size for a long position based on orderbook
        raise NotImplementedError()

    def get_sell_price_from_orderbook(self, orderbook: OrderBook) -> float:
        # Returns the price for a short position based on orderbook
        raise NotImplementedError()

    def get_sell_size_from_orderbook(self, orderbook: OrderBook) -> float:
        # Returns the size for a short position based on orderbook
        raise NotImplementedError()

if __name__ == "__main__":
    pass