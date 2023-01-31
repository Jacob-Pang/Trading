import math
import numpy as np

from collections.abc import Iterable
from sympy import exp, Function, Symbol
from sympy import ln, pi, Matrix
from sympy.stats import density, LogNormal
from .. import PriceModelBase
from ..price_model_interface import PriceSimulationResults

class GBMPriceModelBase (PriceModelBase):
    def __init__(self, asset_tickers: Iterable[str], asset_spot_prices: Iterable[float],
        asset_ret_drift: Iterable[float], asset_ret_covar_mat: np.ndarray, risk_free_rate: float,
        time_step_size: float = 1, time_stamp: float = None, base_unit_of_time: int = 31104000,
        log_ret_values: bool = False) -> None:
        """
        @param asset_tickers (Iterable[str]): the tickers of the assets in the price model universe.
        @param asset_spot_prices (Iterable[float]): the current prices of the assets.
        @param asset_ret_drift (Iterable[float]): the expected returns (percent change in prices).
        @param asset_ret_covar_mat (np.ndarray): the covariance of the @param asset_ret_drift.
        @param risk_free_rate (str): the borrowing rate of the funding currency.
        @param time_step_size (float, opt): the size per time step, in the units of
                @param base_unit_of_time.
        @param time_stamp (float, opt): the current time_stamp of the model in seconds.
        @param base_unit_of_time (int, opt): the base time unit in seconds.
                days:   86,400
                months (30 day basis):  2,592,000
                years (360 day basis):  31,104,000
        @param log_ret_values (bool, opt): whether the return values for @param asset_ret_drift and
                @param asset_ret_covar_mat have undergone log transformation.
        notes:
            * return values and borrowing rates do not correspond to @param time_step_size but rather
                    one unit of @param base_unit_of_time.
        """
        PriceModelBase.__init__(self, asset_tickers, asset_spot_prices, risk_free_rate,
                time_step_size, time_stamp, base_unit_of_time)
        
        asset_ret_drift = np.array(asset_ret_drift, dtype=float)

        if log_ret_values:
            self.asset_log_ret_drift = asset_ret_drift
            self.asset_log_ret_covar_mat = asset_ret_covar_mat
        else:
            self.asset_log_ret_drift = np.log(asset_ret_drift + 1)
            asset_ret_dt: np.ndarray = np.expand_dims(np.exp(self.asset_log_ret_drift), axis=0)
            self.asset_log_ret_covar_mat = np.log(asset_ret_covar_mat / (asset_ret_dt.T
                    @ asset_ret_dt) + 1)

    # Return (denominated in base_unit_of_time) getters
    def get_log_ret_drift(self, asset_ticker: str) -> float:
        return self.asset_log_ret_drift[self.ticker_to_indexes[asset_ticker]]

    def get_log_ret_covar(self, asset_ticker: str, other_ticker: str) -> float:
        return self.asset_log_ret_covar_mat[self.ticker_to_indexes[asset_ticker],
                self.ticker_to_indexes.get(other_ticker)]
    
    def get_log_ret_volatility(self, asset_ticker: str) -> float:
        return np.sqrt(self.get_log_ret_covar(asset_ticker, asset_ticker))

    # St (denominated in time_step_size) getters
    def get_log_st_mean(self, asset_ticker: str) -> float:
        index = self.ticker_to_indexes[asset_ticker]

        return np.log(self.asset_spot_prices[index]) + (self.asset_log_ret_drift[index]
                - self.asset_log_ret_covar_mat[index, index] / 2) \
                * self.get_time_step_size()

    def get_log_st_volatility(self, asset_ticker: str) -> float:
        return np.sqrt(self.get_log_ret_covar(asset_ticker, asset_ticker)
                * self.get_time_step_size()) 

    def get_log_st_covar(self, asset_ticker: str, other_ticker: str) -> float:
        return self.get_time_step_size() * self.get_log_ret_covar(asset_ticker, other_ticker)

    def get_log_st_corr(self, asset_ticker: str, other_ticker: str) -> float:
        return self.get_log_ret_covar(asset_ticker, other_ticker) \
                / self.get_log_ret_volatility(asset_ticker) \
                / self.get_log_ret_volatility(other_ticker)

    # Desnity function getters
    def get_asset_density_fn(self, asset_ticker: str) -> Function:
        dist = LogNormal(Symbol(asset_ticker), mean=self.get_log_st_mean(asset_ticker),
                std=self.get_log_st_volatility(asset_ticker))
        
        return density(dist)(Symbol(asset_ticker))

    def get_joint_density_fn(self, asset_tickers: set[str]) -> Function:
        asset_tickers = list(asset_tickers)
        m = len(asset_tickers)

        if m == 0:  return 1
        if m == 1:  return self.get_asset_density_fn(*asset_tickers)

        # Generate Ln(S_t) covariance matrix
        log_st_covar: Matrix = Matrix.zeros(m, m)

        for i in range(m):
            log_st_covar[i, i] = self.get_log_st_covar(asset_tickers[i], asset_tickers[i])

            for j in range(i + 1, m):
                log_st_covar[i, j] = self.get_log_st_covar(asset_tickers[i], asset_tickers[j])
                log_st_covar[j, i] = log_st_covar[i, j]

        # Generate (Ln(S_t) - E[Ln(S_t)]) vector
        log_st_sub_mu: Matrix = Matrix([
            (ln(Symbol(asset_ticker)) - self.get_log_st_mean(asset_ticker))
            for asset_ticker in asset_tickers
        ])

        return (2 * pi) ** (- m / 2) * (log_st_covar.det()) ** (-0.5) * math.prod(
                    1 / Symbol(asset_ticker) for asset_ticker in asset_tickers
                ) * exp(-0.5 * log_st_sub_mu.T * log_st_covar.inv() * log_st_sub_mu)

    def simulate_prices(self, paths: int, time_steps: int) -> PriceSimulationResults:
        log_st_drift_mean = (self.asset_log_ret_drift - np.diag(self.asset_log_ret_covar_mat) / 2) \
                * self.get_time_step_size()

        # (time_steps, paths, m_assets)
        results = np.random.multivariate_normal(log_st_drift_mean, self.asset_log_ret_covar_mat
                * self.time_step_size, size=(time_steps, paths))
        
        results = np.cumsum(results, axis=0)
        results += np.log(self.asset_spot_prices)
        results = np.exp(results)

        # Append spot prices to results -> (time_steps + 1, paths, m_assets)
        spot_prices = np.full((1, paths, self.asset_spot_prices.size), self.asset_spot_prices)
        results = np.concatenate([spot_prices, results], axis=0)

        # (time_steps, paths, m_assets) -> (m_assets, time_steps + 1, paths)
        results = results.transpose((2, 0, 1))

        return PriceSimulationResults(self.ticker_to_indexes, results)

if __name__ == "__main__":
    pass