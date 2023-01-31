import numpy as np

from scipy.stats import norm
from sympy import exp, Function, Max
from sympy.stats import cdf, Normal

from . import GBMOptionPriceDistributionBase
from .. import GBMAssetPriceDistribution
from ....distribution import DistributionBase
from ....price_distribution.option import CallOptionPriceDistributionBase
from ....price_model_interface import PriceSimulationResults

class GBMCallOptionPriceDistribution (GBMOptionPriceDistributionBase, CallOptionPriceDistributionBase):
    def get_fn(self) -> Function:
        if self.dt > 0:
            z_cdf = cdf(Normal('z', 0, 1))
            return self.st * z_cdf(self.d_1t) - self.K * exp(-self.r * self.dt) * z_cdf(self.d_2t)
        
        return Max(self.st - self.K, 0)

    def get_expectation(self) -> float:
        return self.s0 * np.exp(self.log_ret_mean * self.t) * self.n_d_3 \
                - self.K * np.exp(-self.r * self.dt) * self.n_d_4

    def get_covariance(self, other: DistributionBase) -> float:        
        if not isinstance(other, GBMAssetPriceDistribution):
            # PortfolioDistribution | ReturnDistribution
            return other.get_covariance(self)
        
        log_st_covar = self.price_model.get_log_st_covar(self.asset_ticker, other.asset_ticker)

        if log_st_covar == 0 or self.t == 0:
            # Short circuit for trivial solution.
            return 0

        if not isinstance(other, GBMOptionPriceDistributionBase):
            # AssetPriceDistribution
            return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * self.t) * (
                    np.exp(log_st_covar) * self.n_d_5(log_st_covar) - self.n_d_3
                ) - other.s0 * self.K * np.exp(other.log_ret_mean * self.t - self.r * self.dt) * (
                    self.n_d_6(log_st_covar) - self.n_d_4
                )

        log_st_corr = self.price_model.get_log_st_corr(self.asset_ticker, other.asset_ticker)

        if isinstance(other, GBMCallOptionPriceDistribution):
            return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * self.t) * (
                        np.exp(log_st_covar) * (
                            0.5 * (self.n_d_5(log_st_covar) + other.n_d_5(log_st_covar))
                            + self.H(self, other, self.d_5(log_st_covar), other.d_5(log_st_covar), log_st_corr)
                        )
                        - self.n_d_3 * other.n_d_3
                    ) - self.K * other.s0 * np.exp(other.log_ret_mean * other.t - self.r * self.dt) * (
                        0.5 * (other.n_d_3 + self.n_d_6(log_st_covar))
                        + self.H(other, self, other.d_3, self.d_6(log_st_covar), log_st_corr)
                        - self.n_d_4 * other.n_d_3
                    ) - other.K * self.s0 * np.exp(self.log_ret_mean * self.t - other.r * other.dt) * (
                        0.5 * (self.n_d_3 + other.n_d_6(log_st_covar))
                        + self.H(self, other, self.d_3, other.d_6(log_st_covar), log_st_corr)
                        - self.n_d_3 * other.n_d_4
                    ) + self.K * other.K * np.exp(-(self.r * self.dt + other.r * other.dt)) * (
                    0.5 * (self.n_d_4 + other.n_d_4)
                    + self.H(self, other, self.d_4, other.d_4, log_st_corr)
                    - self.n_d_4 * other.n_d_4
                )

        # PutOptionPriceDistribution
        return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * self.t) * (
                    np.exp(log_st_covar) * (
                        0.5 * (other.n_d_5(log_st_covar) - self.n_d_5(log_st_covar))
                        + self.H(self, other, self.d_5(log_st_covar), other.d_5(log_st_covar), log_st_corr)
                    )
                    + self.n_d_3 * (1 - other.n_d_3)
                ) - self.K * other.s0 * np.exp(other.log_ret_mean * other.t - self.r * self.dt) * (
                    0.5 * (other.n_d_3 - self.n_d_6(log_st_covar))
                    + self.H(other, self, other.d_3, self.d_6(log_st_covar), log_st_corr)
                    + self.n_d_4 * (1 - other.n_d_3)
                ) - other.K * self.s0 * np.exp(self.log_ret_mean * self.t - other.r * other.dt) * (
                    0.5 * (self.n_d_3 + other.n_d_6(log_st_covar))
                    + self.H(self, other, self.d_3, other.d_6(log_st_covar), log_st_corr)
                    - self.n_d_3 * other.n_d_4
                ) + self.K * other.K * np.exp(-(self.r * self.dt + other.r * other.dt)) * (
                    0.5 * (self.n_d_4 + other.n_d_4)
                    + self.H(self, other, self.d_4, other.d_4, log_st_corr)
                    - self.n_d_4 * other.n_d_4
                )

    def get_simulated_values(self, st: PriceSimulationResults) -> np.ndarray:
        """ @returns simulated_prices (np.ndarray): the prices (time_steps x paths) in the results
                corresponding to the @param asset_ticker.
        """
        st: np.ndarray = st.get_simulated_prices(self.asset_ticker)

        # Generating stepwise dt
        dt = np.full(st.shape, -self.t, dtype=float)
        dt = np.cumsum(dt, axis=0)
        dt += (self.T + self.t)
        
        ct = np.empty(st.shape)
        dt_mask = dt > 0
        
        if self.log_ret_volatility > 0:
            d_1 = (np.log(st[dt_mask]) - np.log(self.K) + (self.r + self.log_ret_variance / 2) * dt[dt_mask]) \
                    / (self.log_ret_volatility * np.sqrt(dt[dt_mask]))

            d_2 = d_1 - self.log_ret_volatility * np.sqrt(dt[dt_mask])

            ct[dt_mask] = st[dt_mask] * norm.cdf(d_1) - self.K * np.exp(- self.r * dt[dt_mask]) * norm.cdf(d_2)
        else:
            ct[dt_mask] = st[dt_mask] - self.K * np.exp(- self.r * dt[dt_mask])
        
        ct[dt <= 0] = np.maximum(st[dt <= 0] - self.K, 0)

        return ct

if __name__ == "__main__":
    pass