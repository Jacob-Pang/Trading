from datetime import datetime

from . import AssetBalance
from ...price_model import PriceModelBase
from ...price_model.price_distribution.derivative import DerivativePriceDistributionBase

class DerivativeBalance (AssetBalance):
    def __init__(self, size: float, entry_price: float, asset_ticker: str, expiry_datetime: float,
        derivative_ticker: str = None) -> None:
        """
        @param expiry_datetime (float): the expiration datetime in seconds since epoch.
        """
        AssetBalance.__init__(self, size, entry_price, derivative_ticker)
        self._asset_ticker = asset_ticker
        self.expiry_datetime = expiry_datetime

    # Properties
    @property
    def asset_ticker(self) -> str:
        return self._asset_ticker

    # Getters
    def get_price_dist(self, price_model: PriceModelBase) -> DerivativePriceDistributionBase:
        raise NotImplementedError()

if __name__ == "__main__":
    pass