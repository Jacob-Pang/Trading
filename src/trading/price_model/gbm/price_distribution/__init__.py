import numpy as np

from ..gbm_price_model_base import GBMPriceModelBase
from ...price_distribution import AssetPriceDistributionBase
from ...price_distribution.derivative import DerivativePriceDistributionBase
from ...temporal_distribution import TemporalDistributionBase

class GBMAssetPriceDistribution (AssetPriceDistributionBase):
    price_model: GBMPriceModelBase

    @property
    def log_ret_mean(self) -> float:
        return self.price_model.get_log_ret_drift(self.asset_ticker)

    @property
    def log_ret_variance(self) -> float:
        return self.price_model.get_log_ret_covar(self.asset_ticker, self.asset_ticker)

    @property
    def log_ret_volatility(self) -> float:
        return self.price_model.get_log_ret_volatility(self.asset_ticker)

    def get_log_st_mean(self, t: float = 1) -> float:
        return self.price_model.get_log_st_mean(self.asset_ticker, t)

    def get_log_st_variance(self, t: float = 1) -> float:
        return self.price_model.get_log_st_covar(self.asset_ticker, self.asset_ticker, t)

    def get_log_st_volatility(self, t: float = 1) -> float:
        return self.price_model.get_log_st_volatility(self.asset_ticker, t)

    def get_expectation(self, t: float = 1) -> float:
        return self.s0 * np.exp(self.log_ret_mean * t)

    def get_variance(self, t: float = 1) -> float:
        return self.s0 ** 2 * np.exp(2 * self.log_ret_mean * t) * \
                (np.exp(self.get_log_st_variance(t)) - 1)

    def get_covariance(self, other: TemporalDistributionBase, t: float = 1) -> float:
        if not isinstance(other, GBMAssetPriceDistribution) or \
            isinstance(other, DerivativePriceDistributionBase):
            # DerivativePriceDistribution | PortfolioDistribution | ReturnDistribution
            return other.get_covariance(self, t)

        return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * t) * (
            np.exp(self.price_model.get_log_st_covar(self.asset_ticker, other.asset_ticker, t))
            - 1
        )

if __name__ == "__main__":
    pass