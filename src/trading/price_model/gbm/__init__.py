from .gbm_price_model_base import GBMPriceModelBase
from .price_distribution import GBMAssetPriceDistribution
from .price_distribution.option.call_option import GBMCallOptionPriceDistribution
from .price_distribution.option.put_option import GBMPutOptionPriceDistribution

class GBMPriceModel (GBMPriceModelBase):
    # PriceDistribution generators
    def get_asset_price_dist(self, asset_ticker: str) -> GBMAssetPriceDistribution:
        assert asset_ticker in self.ticker_to_indexes
        return GBMAssetPriceDistribution(self, asset_ticker)

    def get_call_option_price_dist(self, asset_ticker: str, strike_price: float,\
        time_to_expiry: float, option_ticker: str = None) \
        -> GBMCallOptionPriceDistribution:
        assert asset_ticker in self.ticker_to_indexes
        return GBMCallOptionPriceDistribution(self, asset_ticker, strike_price,
                time_to_expiry, option_ticker)

    def get_put_option_price_dist(self, asset_ticker: str, strike_price: float,\
        time_to_expiry: float, option_ticker: str = None) \
        -> GBMPutOptionPriceDistribution:
        assert asset_ticker in self.ticker_to_indexes
        return GBMPutOptionPriceDistribution(self, asset_ticker, strike_price,
                time_to_expiry, option_ticker)

if __name__ == "__main__":
    pass