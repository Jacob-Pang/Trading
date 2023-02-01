import numpy as np

from sympy import Function
from sympy import ln, sqrt
from scipy.special import owens_t

from .. import GBMAssetPriceDistribution
from ....price_distribution.option import OptionPriceDistributionBase

class GBMOptionPriceDistributionBase (OptionPriceDistributionBase, GBMAssetPriceDistribution):
    @staticmethod
    def H(a: "GBMOptionPriceDistributionBase", b: "GBMOptionPriceDistributionBase", d_ai: float,
        d_bj: float, log_st_corr: float, t: float) -> float:

        def sign_plus(v: float) -> int:
            return -1 if v < 0 else 1

        dt_a, dt_b = a.get_dt(t), b.get_dt(t)
        owens_t_h_scalar = 1 / np.sqrt(a.T * b.T - log_st_corr ** 2 * t ** 2)
        eta = d_bj * np.sqrt(b.T) - log_st_corr * d_ai * np.sqrt(a.T)

        return 0.5 * np.sign(log_st_corr) * (
                int(np.sign(log_st_corr) * sign_plus(eta) * sign_plus(-d_ai) < 0)
                + int(sign_plus(-log_st_corr * eta) * sign_plus(-log_st_corr * d_bj) < 0)
                - int(log_st_corr > 0)
            ) - (
                0.5 * np.sign(d_ai * np.sqrt(a.T) / dt_a + log_st_corr * d_bj * np.sqrt(b.T)
                        / (dt_b + (1 - log_st_corr ** 2) * t)) if eta == 0 else 0
            ) \
            - owens_t(d_ai, owens_t_h_scalar * (d_bj / d_ai * np.sqrt(a.T * b.T) - log_st_corr * t)) \
            - owens_t(d_bj, owens_t_h_scalar * (d_ai / d_bj * np.sqrt(a.T * b.T) - log_st_corr * t))

    def get_d1_t(self, dt: float) -> Function:
        return (ln(self.st) - ln(self.K) + (self.r + self.log_ret_variance / 2) * dt) \
                / (self.log_ret_volatility * sqrt(dt))

    def get_d2_t(self, dt: float) -> Function:
        return self.get_d1_t(dt) - self.log_ret_volatility * sqrt(dt)

    def get_d3(self, t: float) -> float:
        if self.log_ret_volatility == 0 or self.T == 0:
            return np.inf

        return (np.log(self.s0) - np.log(self.K) + self.log_ret_mean * t
                + self.r * self.get_dt(t) + self.log_ret_variance / 2 * self.T) \
                / (self.log_ret_volatility * np.sqrt(self.T))

    def get_d4(self, d3: float) -> float:
        if np.isposinf(d3):
            return np.inf
        
        return d3 - self.log_ret_volatility * np.sqrt(self.T)

    def get_d5(self, d3: float, log_st_covar: float) -> float:
        if np.isposinf(d3):
            return np.inf

        return d3 + log_st_covar / (self.log_ret_volatility * np.sqrt(self.T))

    def get_d6(self, d5: float) -> float:
        if np.isposinf(d5):
            return np.inf

        return d5 - self.log_ret_volatility * np.sqrt(self.T)

    def get_variance(self, t: float = 1) -> float:
        return self.get_covariance(self, t)

    def get_plot_range_dist_params(self, t: float = 1) -> tuple[float, float]:
        return (GBMAssetPriceDistribution.get_expectation(self, t), np.sqrt(GBMAssetPriceDistribution
                .get_variance(self, t)))

if __name__ == "__main__":
    pass