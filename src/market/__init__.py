from ..balances import Balances

class PositionBase:
    def __init__(self, market: "MarketBase", entry_price: float, balances: Balances) -> None:
        self.market = market
        self.avg_price = entry_price
        self.balances = balances

    @property
    def open(self) -> bool:
        # Margin of error for floating point arithmetic errors
        return abs(self.get_open_size()) > 0.0001

    @property
    def closed(self) -> bool:
        return not self.open

    @property
    def short(self) -> bool:
        # Returns whether the position is a short one
        return self.get_open_size() < 0

    def assimilate(self, other_position: "PositionBase") -> None:
        open_size = self.get_open_size()
        other_size = other_position.get_open_size()
        net_size = open_size + other_size
        
        self.avg_price = (self.avg_price * open_size + other_position.avg_price * other_size) \
                / (open_size + other_size) if net_size else None

        self.balances.assimilate(other_position.balances)
        
    def get_open_size(self) -> float:
        # Returns the opened size of the position
        raise NotImplementedError()

    def get_closing_size(self, transact_fee_rate: float) -> float:
        # Returns the size to close this position accounting for transaction fees
        return self.market.get_contra_position_size(self.get_open_size(), transact_fee_rate)

class MarketBase:
    def __init__(self) -> None:
        # Reduce overhead by storing the attributes
        self.ticker = self.get_ticker()
        self.query = self.get_query()

    def get_ticker(self) -> str:
        raise NotImplementedError()

    def get_query(self) -> str:
        # Returns the query string for the URL
        return None

    def get_funding_currency(self) -> str:
        # Returns the ticker for the funding currency for the market.
        raise NotImplementedError()

    def get_contra_position_size(self, size: float, transact_fee_rate: float) -> float:
        # Returns the contra_position size for an exisiting position size and transact_fee_rate.
        # Note negative sizes -> short position
        return - size

    def open_position(self, entry_price: float, size: float, transact_fee_rate: float,
        as_contra_position: bool = False) -> PositionBase:
        """ Opens a position.

        @param entry_price (float): The average price at which to open the position.
        @param size (float): The number of contracts or size of position to open, where
                negative sizes indicate a short position.
        @param transact_fee_rate (float): The transaction fee as percentage of trade value.
        @param as_contra_position (bool, opt = False): Whether to open a contra-position
                to an existing_position (size = @param size) instead.
                True: @param size is treated as the open_size for the existing_position, and
                        the size to open is given by @method MarketBase.get_contra_position_size.
                False: @param size is treated as the size to open.

        @returns open_position (PositionBase): The position generated from the transaction.
                If as_contra_position, perform exsiting_position.assimilate(contra_position)
                to close the exisitng_position.
        """
        raise NotImplementedError()

    def get_tradeable_funds(self, balances: Balances) -> float:
        # Returns the size of funds tradeable on the market
        raise NotImplementedError()

if __name__ == "__main__":
    pass
