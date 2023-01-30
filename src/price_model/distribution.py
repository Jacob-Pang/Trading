import numpy as np

from copy import copy
from collections import defaultdict
from scipy.stats import norm
from sympy import Function, Symbol
from sympy import plot, plot_parametric
from uuid import uuid4
from .price_model_interface import PriceSimulationResults

class DistributionBase:
    # Characteristic functions
    def get_fn(self) -> Function:
        raise NotImplementedError()

    def get_density_fn(self) -> Function:
        raise NotImplementedError()

    # Distribution parameters
    def get_expectation(self) -> float:
        raise NotImplementedError()
    
    def get_variance(self) -> float:
        raise NotImplementedError()
    
    def get_covariance(self, other: "DistributionBase") -> float:
        raise NotImplementedError()

    # Simulation methods
    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        raise NotImplementedError()

    # Plotting methods
    def get_plot_xvar(self) -> Symbol:
        raise NotImplementedError()

    def get_plot_fn_label(self) -> str:
        raise NotImplementedError()
    
    def get_plot_range_dist_params(self) -> tuple[float, float]:
        """ @returns range_dist_params (tuple[float, float]): the mean and standard
                deviation of the plotting range distribution.
        """
        return (self.get_expectation(), np.sqrt(self.get_variance()))

    def plot(self, tail_percentile: float = .025, density_weighted: bool = False, offset: float = 0.):
        xvar = self.get_plot_xvar()
        mean, std = self.get_plot_range_dist_params()
        plot_range = (xvar, max(0, norm.ppf(tail_percentile, loc=mean, scale=std)),
                norm.ppf(1 - tail_percentile, loc=mean, scale=std))

        fn = self.get_fn() + offset
        fn_plot = plot(fn, plot_range, label=self.get_plot_fn_label(),
                show=False, legend=True)

        fn_plot.extend(plot_parametric((xvar, self.get_expectation() + offset), plot_range,
                label="mean", show=False, legend=True))

        if density_weighted:
            density_fn = self.get_density_fn()

            fn_plot.extend(plot(density_fn, plot_range, label="price_density_fn",
                    show=False, legend=True))
            fn_plot.extend(plot(density_fn * fn, plot_range, label="density_weighted",
                    show=False, legend=True))

        fn_plot.show()
        return fn_plot

class AssetDistributionBase (DistributionBase):
    def __init__(self, ticker: str = None) -> None:
        # @param ticker (str): the identifying ticker, generates an UUID by default.
        self.ticker = ticker if ticker else uuid4()

    @property
    def asset_ticker(self) -> str:
        return self.ticker

class PortfolioDistributionBase (DistributionBase):
    def __init__(self) -> None:
        self.ticker_to_dists = dict[str, AssetDistributionBase]()
        self.ticker_to_sizes: dict[str, float] = defaultdict(float)

    def add(self, dist: AssetDistributionBase, size: float) -> None:
        if dist.ticker in self.ticker_to_sizes:
            self.ticker_to_sizes[dist.ticker] += size
        else:
            self.ticker_to_dists[dist.ticker] = copy(dist)
            self.ticker_to_sizes[dist.ticker] = size

    def get_dist_weight(self, ticker: str) -> float:
        raise NotImplementedError()

    # Characteristic functions
    def get_fn(self) -> Function:
        return sum(self.get_dist_weight(ticker) * dist.get_fn() for ticker, dist
                in self.ticker_to_dists.items())
    
    def get_density_fn(self) -> Function:
        raise NotImplementedError()

    # Distribution parameters
    def get_expectation(self) -> float:
        return sum(self.ticker_to_sizes.get(ticker) * dist.get_expectation() for ticker, dist
                in self.ticker_to_dists.items())

    def get_variance(self) -> float:
        tickers = list(self.ticker_to_dists.keys())
        m = len(tickers)
        portfolio_var = 0

        for i in range(m):
            dist_a = self.ticker_to_dists.get(tickers[i])
            weight_a = self.get_dist_weight(tickers[i])
            portfolio_var += weight_a ** 2 * dist_a.get_variance()

            for j in range(i + 1, m):
                dist_b = self.ticker_to_dists.get(tickers[j])
                weight_b = self.get_dist_weight(tickers[j])
                portfolio_var += 2 * weight_a * weight_b * dist_a.get_covariance(dist_b)

        return portfolio_var

    def get_covariance(self, other: DistributionBase) -> float:
        if isinstance(other, PortfolioDistributionBase):
            cached_values = dict[tuple[str, str], float]()
            portfolio_covar = 0

            for ticker_a, dist_a in self.ticker_to_dists.items():
                weight_a = self.get_dist_weight(ticker_a)

                for ticker_b, dist_b in other.ticker_to_dists.items():
                    weight_b = other.get_dist_weight(ticker_b)

                    if (weight_a, weight_b) not in cached_values:
                        cached_values[(weight_a, weight_b)] = dist_a.get_covariance(dist_b)
                        cached_values[(weight_b, weight_a)] = cached_values[(weight_a, weight_b)]

                    portfolio_covar += weight_a * weight_b * cached_values.get((weight_a, weight_b))
                    
            return portfolio_covar

        return sum(self.get_dist_weight(ticker) * dist.get_covariance(other)
                for ticker, dist in self.ticker_to_dists.items())

    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        return sum(self.get_dist_weight(ticker) * dist.get_simulated_values(results)
                for ticker, dist in self.ticker_to_dists.items())

    def get_weight_vect(self) -> np.ndarray:
        return np.array([self.get_dist_weight(ticker) for ticker in self.ticker_to_dists], dtype=float)

    def get_expectation_vect(self) -> np.ndarray:
        return np.array([dist.get_expectation() for dist in self.ticker_to_dists.values()], dtype=float)

    def get_covar_mat(self) -> np.ndarray:
        dists = list(self.ticker_to_dists.values())
        m = len(dists)
        portfolio_covar_mat = np.empty(shape=(m, m), dtype=float)

        for i in range(m):
            portfolio_covar_mat[i, i] = dists[i].get_variance()

            for j in range(i + 1, m):
                portfolio_covar_mat[i, j] = dists[i].get_covariance(dists[j])
                portfolio_covar_mat[j, i] = portfolio_covar_mat[i, j] 

        return portfolio_covar_mat

    def get_simulated_values_vect(self, results: PriceSimulationResults) -> np.ndarray:
        return np.stack([dist.get_simulated_values(results) for dist
                in self.ticker_to_dists.values()], axis=0)

    # Plotting methods
    def get_plot_xvar(self) -> Symbol:
        asset_tickers = { dist.asset_ticker for dist in self.ticker_to_dists.values() }
        assert len(asset_tickers) == 1, "Multivariate functions cannot be plotted on 2D axis."
        return list(asset_tickers)[0]
    
    def get_plot_range_dist_params(self) -> tuple[float, float]:
        """ @returns range_dist_params (tuple[float, float]): the mean and standard
                deviation of the plotting range distribution.
        """
        return list(self.ticker_to_dists.values())[0].get_plot_range_dist_params()

if __name__ == "__main__":
    pass