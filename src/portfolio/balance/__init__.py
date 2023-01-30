from uuid import uuid4

from ...price_model import PriceModelBase
from ...price_model.price_distribution import AssetPriceDistributionBase
from ...price_model.return_distribution import AssetReturnDistribution

class AssetBalance:
    def __init__(self, size: float, entry_price: float, ticker: str = None) -> None:
        self.ticker = ticker if ticker else uuid4()
        self.size = size
        self.entry_price = entry_price

    # Properties
    @property
    def asset_ticker(self) -> str:
        return self.ticker
    
    @property
    def short(self) -> bool:
        return self.size < 0

    # Getters
    def get_entry_cost(self) -> float:
        return self.size * self.entry_price

    def get_price_dist(self, price_model: PriceModelBase) -> AssetPriceDistributionBase:
        return price_model.get_asset_price_dist(self.asset_ticker)

    def get_ret_dist(self, price_model: PriceModelBase) -> AssetReturnDistribution:
        return AssetReturnDistribution(self.get_price_dist(price_model), self.entry_price)

    def __repr__(self) -> str:
        return str(self.size)

    # Mutators
    def assimilate(self, other: "AssetBalance") -> None:
        assert self.ticker == other.ticker

        net_entry_cost = self.get_entry_cost() + other.get_entry_cost()
        self.size += other.size
        self.entry_price = net_entry_cost / self.size if self.size else 0

if __name__ == "__main__":
    pass