import numpy as np

from sympy import Function
from sympy import ln, sqrt
from scipy.stats import norm
from scipy.special import owens_t

from .. import GBMAssetPriceDistribution
from ....price_distribution.option import OptionPriceDistributionBase

class GBMOptionPriceDistributionBase (OptionPriceDistributionBase, GBMAssetPriceDistribution):
    # Cached values
    _d_3  : float = None
    _d_4  : float = None
    _n_d_3: float = None
    _n_d_4: float = None

    @staticmethod
    def H(a: "GBMOptionPriceDistributionBase", b: "GBMOptionPriceDistributionBase", d_ai: float,
        d_bj: float, log_st_corr: float) -> float:

        def sign_plus(v: float) -> int:
            return -1 if v < 0 else 1

        owens_t_h_scalar = 1 / np.sqrt(a.T * b.T - log_st_corr ** 2 * a.t ** 2)
        eta = d_bj * np.sqrt(b.T) - log_st_corr * d_ai * np.sqrt(a.T)

        return 0.5 * np.sign(log_st_corr) * (
                int(np.sign(log_st_corr) * sign_plus(eta) * sign_plus(-d_ai) < 0)
                + int(sign_plus(-log_st_corr * eta) * sign_plus(-log_st_corr * d_bj) < 0)
                - int(log_st_corr > 0)
            ) - (
                0.5 * np.sign(d_ai * np.sqrt(a.T) / a.dt + log_st_corr * d_bj * np.sqrt(b.T)
                        / (b.dt + (1 - log_st_corr ** 2) * b.t)) if eta == 0 else 0
            ) \
            - owens_t(d_ai, owens_t_h_scalar * (d_bj / d_ai * np.sqrt(a.T * b.T) - log_st_corr * a.t)) \
            - owens_t(d_bj, owens_t_h_scalar * (d_ai / d_bj * np.sqrt(a.T * b.T) - log_st_corr * a.t))

    @property
    def d_1t(self) -> Function:
        return (ln(self.st) - ln(self.K) + (self.r + self.log_ret_variance / 2) * self.dt) \
                / (self.log_ret_volatility * sqrt(self.dt))

    @property
    def d_2t(self) -> Function:
        return self.d_1t - self.log_ret_volatility * sqrt(self.dt)

    @property
    def d_3(self) -> float:
        if self._d_3 is None:
            self._d_3 = (np.log(self.s0) - np.log(self.K) + self.log_ret_mean * self.t + self.r * self.dt
                    + self.log_ret_variance / 2 * self.T) / (self.log_ret_volatility * np.sqrt(self.T))

        return self._d_3

    @property
    def d_4(self) -> float:
        if self._d_4 is None:
            self._d_4 = self.d_3 - self.log_ret_volatility * np.sqrt(self.T)
        
        return self._d_4

    def d_5(self, log_st_covar: float) -> float:
        return self.d_3 + log_st_covar / (self.log_ret_volatility * np.sqrt(self.T))

    def d_6(self, log_st_covar: float) -> float:
        return self.d_5(log_st_covar) - self.log_ret_volatility * np.sqrt(self.T)

    @property
    def n_d_3(self) -> float:
        if self._n_d_3 is None:
            self._n_d_3 = 1 if (self.log_ret_volatility == 0 or self.T == 0) else norm.cdf(self.d_3) 
            
        return self._n_d_3

    @property
    def n_d_4(self) -> float:
        if self._n_d_4 is None:
            self._n_d_4 = 1 if (self.log_ret_volatility == 0 or self.T == 0) else norm.cdf(self.d_4)

        return self._n_d_4

    def n_d_5(self, log_st_covar: float) -> float:
        if (self.log_ret_volatility == 0 or self.T == 0):
            return 1

        return norm.cdf(self.d_5(log_st_covar))

    def n_d_6(self, log_st_covar: float) -> float:
        if (self.log_ret_volatility == 0 or self.T == 0):
            return 1

        return norm.cdf(self.d_6(log_st_covar))

    def get_variance(self) -> float:
        return self.get_covariance(self)

    def get_plot_range_dist_params(self) -> tuple[float, float]:
        return (GBMAssetPriceDistribution.get_expectation(self), np.sqrt(GBMAssetPriceDistribution
                .get_variance(self)))

if __name__ == "__main__":
    pass