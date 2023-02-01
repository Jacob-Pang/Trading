import numpy as np

from scipy.stats import norm
from sympy import exp, Function, Max
from sympy.stats import cdf, Normal

from . import GBMOptionPriceDistributionBase
from .. import GBMAssetPriceDistribution
from ....temporal_distribution import TemporalDistributionBase
from ....price_distribution.option import CallOptionPriceDistributionBase
from ....price_model_interface import PriceSimulationResults

class GBMCallOptionPriceDistribution (GBMOptionPriceDistributionBase, CallOptionPriceDistributionBase):
    def get_fn(self, t: float = 1) -> Function:
        dt = self.get_dt(t)

        if dt > 0:
            z_cdf = cdf(Normal('z', 0, 1))
            return self.st * z_cdf(self.get_d1_t(dt)) - self.K * exp(-self.r * dt) \
                    * z_cdf(self.get_d2_t(dt))
        
        return Max(self.st - self.K, 0)

    def get_expectation(self, t: float = 1, d3: float = None, d4: float = None) -> float:
        if d3 is None:  d3 = self.get_d3(t)
        if d4 is None:  d4 = self.get_d4(d3)

        return self.s0 * np.exp(self.log_ret_mean * t) * norm.cdf(d3) - self.K \
                * np.exp(-self.r * self.get_dt(t)) * norm.cdf(d4)

    def get_covariance(self, other: TemporalDistributionBase, t: float = 1) -> float:        
        if not isinstance(other, GBMAssetPriceDistribution):
            # PortfolioDistribution | ReturnDistribution
            return other.get_covariance(self, t)
        
        log_st_covar = self.price_model.get_log_st_covar(self.asset_ticker, other.asset_ticker, t)

        if log_st_covar == 0 or t == 0:
            # Short circuit for trivial solution.
            return 0

        dt_a = self.get_dt(t)
        d3_a = self.get_d3(t)
        d4_a = self.get_d4(d3_a)
        d5_a = self.get_d5(d3_a, log_st_covar)
        d6_a = self.get_d6(d5_a)

        nd3_a = norm.cdf(d3_a)
        nd4_a = norm.cdf(d4_a)

        if not isinstance(other, GBMOptionPriceDistributionBase):
            # AssetPriceDistribution
            return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * t) * (
                    np.exp(log_st_covar) * norm.cdf(d5_a) - nd3_a
                ) - other.s0 * self.K * np.exp(other.log_ret_mean * t - self.r * dt_a) * (
                    norm.cdf(d6_a) - nd4_a
                )

        log_st_corr = self.price_model.get_log_st_corr(self.asset_ticker, other.asset_ticker)
        dt_b = other.get_dt(t)
        d3_b = other.get_d3(t)
        d4_b = other.get_d4(d3_b)
        d5_b = other.get_d5(d3_b, log_st_covar)
        d6_b = other.get_d6(d5_b)

        nd3_b = norm.cdf(d3_b)
        nd4_b = norm.cdf(d4_b)

        if isinstance(other, GBMCallOptionPriceDistribution):
            return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * t) * (
                        np.exp(log_st_covar) * (
                            0.5 * (norm.cdf(d5_a) + norm.cdf(d5_b))
                            + GBMOptionPriceDistributionBase.H(self, other, d5_a, d5_b, log_st_corr, t)
                        ) - nd3_a * nd3_a
                    ) - self.K * other.s0 * np.exp(other.log_ret_mean * t - self.r * dt_a) * (
                        0.5 * (nd3_b + norm.cdf(d6_a))
                        + GBMOptionPriceDistributionBase.H(other, self, d3_b, d6_a, log_st_corr, t)
                        - nd4_a * nd3_b
                    ) - other.K * self.s0 * np.exp(self.log_ret_mean * t - other.r * dt_b) * (
                        0.5 * (nd3_a + norm.cdf(d6_b))
                        + GBMOptionPriceDistributionBase.H(self, other, d3_a, d6_b, log_st_corr, t)
                        - nd3_a * nd4_b
                    ) + self.K * other.K * np.exp(-(self.r * dt_a + other.r * dt_b)) * (
                    0.5 * (nd4_a + nd4_b)
                    + GBMOptionPriceDistributionBase.H(self, other, d4_a, d4_b, log_st_corr, t)
                    - nd4_a * nd4_b
                )

        # PutOptionPriceDistribution
        return self.s0 * other.s0 * np.exp((self.log_ret_mean + other.log_ret_mean) * t) * (
                    np.exp(log_st_covar) * (
                        0.5 * (norm.cdf(d5_b) - norm.cdf(d5_a))
                        + GBMOptionPriceDistributionBase.H(self, other, d5_a, d5_b, log_st_corr, t)
                    ) + nd3_a * (1 - nd3_b)
                ) - self.K * other.s0 * np.exp(other.log_ret_mean * t - self.r * dt_a) * (
                    0.5 * (nd3_b - norm.cdf(d6_a))
                    + GBMOptionPriceDistributionBase.H(other, self, d3_b, d6_a, log_st_corr, t)
                    + nd4_a * (1 - nd3_b)
                ) - other.K * self.s0 * np.exp(self.log_ret_mean * t - other.r * dt_b) * (
                    0.5 * (nd3_a + norm.cdf(d6_b))
                    + GBMOptionPriceDistributionBase.H(self, other, d3_a, d6_b, log_st_corr, t)
                    - nd3_a * nd4_b
                ) + self.K * other.K * np.exp(-(self.r * dt_a + other.r * dt_b)) * (
                    0.5 * (nd4_a + nd4_b)
                    + GBMOptionPriceDistributionBase.H(self, other, d4_a, d4_b, log_st_corr, t)
                    - nd4_a * nd4_b
                )

    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        """ @returns simulated_prices (np.ndarray): the prices (time_steps x paths) in the results
                corresponding to the @param asset_ticker.
        """
        st: np.ndarray = results.get_simulated_prices(self.asset_ticker)

        # Generating stepwise dt
        dt = np.full(st.shape, - results.t, dtype=float)
        dt = np.cumsum(dt, axis=0)
        dt += (self.T + results.t)
        
        ct = np.empty(st.shape)
        dt_mask = dt > 0
        
        if self.log_ret_volatility > 0:
            d1_t = (np.log(st[dt_mask]) - np.log(self.K) + (self.r + self.log_ret_variance / 2) \
                    * dt[dt_mask]) / (self.log_ret_volatility * np.sqrt(dt[dt_mask]))

            d2_t = d1_t - self.log_ret_volatility * np.sqrt(dt[dt_mask])

            ct[dt_mask] = st[dt_mask] * norm.cdf(d1_t) - self.K * np.exp(- self.r * dt[dt_mask]) \
                    * norm.cdf(d2_t)
        else:
            ct[dt_mask] = st[dt_mask] - self.K * np.exp(- self.r * dt[dt_mask])
        
        ct[dt <= 0] = np.maximum(st[dt <= 0] - self.K, 0)

        return ct

if __name__ == "__main__":
    pass