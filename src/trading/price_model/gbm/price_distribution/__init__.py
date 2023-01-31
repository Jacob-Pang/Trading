import numpy as np

from ..gbm_price_model_base import GBMPriceModelBase
from ...price_distribution import AssetPriceDistributionBase
from ...price_distribution.derivative import DerivativePriceDistributionBase
from ...distribution import DistributionBase

class GBMAssetPriceDistribution (AssetPriceDistributionBase):
    price_model: GBMPriceModelBase

    # Cached values
    _log_st_mean: float  = None

    @property
    def log_ret_mean(self) -> float:
        return self.price_model.get_log_ret_drift(self.asset_ticker)

    @property
    def log_ret_variance(self) -> float:
        return self.price_model.get_log_ret_covar(self.asset_ticker, self.asset_ticker)

    @property
    def log_ret_volatility(self) -> float:
        return self.price_model.get_log_ret_volatility(self.asset_ticker)

    @property
    def log_st_mean(self) -> float:
        if self._log_st_mean is None:
            self._log_st_mean = self.price_model.get_log_st_mean(self.asset_ticker)

        return self._log_st_mean

    @property
    def log_st_variance(self) -> float:
        return self.price_model.get_log_st_covar(self.asset_ticker, self.asset_ticker)

    @property
    def log_st_volatility(self) -> float:
        return self.price_model.get_log_st_volatility(self.asset_ticker)

    def get_expectation(self) -> float:
        return self.s0 * np.exp(self.log_ret_mean * self.t)

    def get_variance(self) -> float:
        return self.s0 ** 2 * np.exp(2 * self.log_ret_mean * self.t) * \
                (np.exp(self.log_st_variance) - 1)

    def get_covariance(self, other: DistributionBase) -> float:
        if not isinstance(other, GBMAssetPriceDistribution) or \
            isinstance(other, DerivativePriceDistributionBase):
            # DerivativePriceDistribution | PortfolioDistribution | ReturnDistribution
            return other.get_covariance(self)

        return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * self.t) * \
                    (np.exp(self.price_model.get_log_st_covar(self.asset_ticker,
                    other.asset_ticker)) - 1)

if __name__ == "__main__":
    pass