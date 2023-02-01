import numpy as np

from copy import copy
from collections import defaultdict
from collections.abc import Iterable
from scipy.stats import norm
from sympy import Function, Symbol
from sympy import plot, plot_parametric
from uuid import uuid4
from .price_model_interface import PriceSimulationResults

class DistributionPlotResults:
    # Container for distribution plots
    _dist_plot = None

    def get(self):
        return self._dist_plot

    def extend(self, fn_plot) -> None:
        if self._dist_plot is None:
            self._dist_plot = fn_plot
        else: # Extend existing plot
            self._dist_plot.extend(fn_plot)

    def show(self) -> None:
        self._dist_plot.show()

class TemporalDistributionBase:
    # Characteristic functions
    def get_fn(self, t: float = 1) -> Function:
        raise NotImplementedError()

    def get_density_fn(self, t: float = 1) -> Function:
        raise NotImplementedError()

    # Distribution parameters
    def get_expectation(self, t: float = 1) -> float:
        raise NotImplementedError()
    
    def get_variance(self, t: float = 1) -> float:
        raise NotImplementedError()
    
    def get_covariance(self, other: "TemporalDistributionBase", t: float = 1) -> float:
        raise NotImplementedError()

    # Simulation methods
    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        raise NotImplementedError()

    # Plotting methods
    def get_plot_xvar(self) -> Symbol:
        raise NotImplementedError()

    def get_plot_fn_label(self) -> str:
        raise NotImplementedError()
    
    def get_plot_range_dist_params(self, t: float = 1) -> tuple[float, float]:
        """ @returns range_dist_params (tuple[float, float]): the mean and standard
                deviation of the plotting range distribution.
        """
        return (self.get_expectation(t), np.sqrt(self.get_variance(t)))

    def plot(self, t: (float | Iterable[float]) = 1, plot_range: tuple[float, float] = None,
        tail_percentile: float = .025, plot_fn: bool = True, plot_expectation: bool = False,
        plot_density_fn: bool = False, plot_density_weighted: bool = False,
        constant_offset: float = 0., show: bool = True) -> DistributionPlotResults:
        """
        @param t (float | Iterable[float], opt): the timestep sizes(s) to plot.
        @param plot_range (tuple[float, float], opt): the range of values to plot.
        @param tail_percentile (float): the percentile of tail values not plotted.
        @param plot_fn (bool, opt): plots the distribution function.
        @param plot_expectation (bool, opt): plots the expectations (horizontal).
        @param plot_density_fn (bool, opt): plots the density function.
        @param plot_density_weighted (bool, opt): plots the distribution function
                weighted by the density function.
        @param constant_offset (bool, opt): adds a constant vertical offset to the
                distribution and expectation functions.
        @param show (bool, opt): shows the plot.

        @returns dist_plot (DistributionPlotResults): container for the plot.

        Notes:
            1. Only supports univariate distributions.
        """
        xvar = self.get_plot_xvar()
        dist_plot = DistributionPlotResults()
        ts: list[float] = [t] if isinstance(t, float) else t

        if not plot_range:
            for t in ts:
                mean, std = self.get_plot_range_dist_params(t)
                min_range = norm.ppf(tail_percentile, loc=mean, scale=std)
                max_range = norm.ppf(1 - tail_percentile, loc=mean, scale=std)

                if not plot_range:
                    plot_range = [min_range, max_range]
                else:
                    plot_range[0] = min(plot_range[0], min_range)
                    plot_range[1] = max(plot_range[1], max_range)

        plot_range = (xvar, max(0.01, plot_range[0]), plot_range[1])

        for t in ts:
            fn, density_fn = None, None

            if plot_fn:
                fn = self.get_fn(t) + constant_offset
                dist_plot.extend(plot(fn, plot_range, label=self.get_plot_fn_label() + f" ({t})",
                        show=False, legend=True))

            if plot_expectation:
                dist_plot.extend(plot_parametric((xvar, self.get_expectation(t) + constant_offset),
                        plot_range, label=f"mean ({t})", show=False, legend=True))

            if plot_density_fn:
                density_fn = self.get_density_fn(t)
                dist_plot.extend(plot(density_fn, plot_range, label=f"price_density_fn ({t})",
                        show=False, legend=True))

            if plot_density_weighted:
                if not fn: fn = self.get_fn(t) + constant_offset
                if not density_fn: density_fn = self.get_density_fn(t)

                dist_plot.extend(plot(density_fn * fn, plot_range, label=f"density_weighted ({t})",
                        show=False, legend=True))

        if show: dist_plot.show()
        return dist_plot

class AssetTemporalDistributionBase (TemporalDistributionBase):
    def __init__(self, ticker: str = None) -> None:
        # @param ticker (str): the identifying ticker, generates an UUID by default.
        self.ticker = ticker if ticker else uuid4()

    @property
    def asset_ticker(self) -> str:
        return self.ticker

class PortfolioTemporalDistributionBase (TemporalDistributionBase):
    def __init__(self) -> None:
        self.ticker_to_dists = dict[str, AssetTemporalDistributionBase]()
        self.ticker_to_sizes: dict[str, float] = defaultdict(float)

    def add(self, dist: AssetTemporalDistributionBase, size: float) -> None:
        if dist.ticker in self.ticker_to_sizes:
            self.ticker_to_sizes[dist.ticker] += size
        else:
            self.ticker_to_dists[dist.ticker] = copy(dist)
            self.ticker_to_sizes[dist.ticker] = size

    def get_dist_weight(self, ticker: str) -> float:
        raise NotImplementedError()

    # Characteristic functions
    def get_fn(self, t: float = 1) -> Function:
        return sum(self.get_dist_weight(ticker) * dist.get_fn(t) for ticker, dist
                in self.ticker_to_dists.items())

    # Distribution parameters
    def get_expectation(self, t: float = 1) -> float:
        return sum(self.ticker_to_sizes.get(ticker) * dist.get_expectation(t) for ticker, dist
                in self.ticker_to_dists.items())

    def get_variance(self, t: float = 1) -> float:
        tickers = list(self.ticker_to_dists.keys())
        m = len(tickers)
        portfolio_var = 0

        for i in range(m):
            dist_a = self.ticker_to_dists.get(tickers[i])
            weight_a = self.get_dist_weight(tickers[i])
            portfolio_var += weight_a ** 2 * dist_a.get_variance(t)

            for j in range(i + 1, m):
                dist_b = self.ticker_to_dists.get(tickers[j])
                weight_b = self.get_dist_weight(tickers[j])
                portfolio_var += 2 * weight_a * weight_b * dist_a.get_covariance(dist_b, t)

        return portfolio_var

    def get_covariance(self, other: TemporalDistributionBase, t: float = 1) -> float:
        if isinstance(other, PortfolioTemporalDistributionBase):
            cached_values = dict[tuple[str, str], float]()
            portfolio_covar = 0

            for ticker_a, dist_a in self.ticker_to_dists.items():
                weight_a = self.get_dist_weight(ticker_a)

                for ticker_b, dist_b in other.ticker_to_dists.items():
                    weight_b = other.get_dist_weight(ticker_b)

                    if (weight_a, weight_b) not in cached_values:
                        cached_values[(weight_a, weight_b)] = dist_a.get_covariance(dist_b, t)
                        cached_values[(weight_b, weight_a)] = cached_values[(weight_a, weight_b)]

                    portfolio_covar += weight_a * weight_b * cached_values.get((weight_a, weight_b))
                    
            return portfolio_covar

        return sum(self.get_dist_weight(ticker) * dist.get_covariance(other, t)
                for ticker, dist in self.ticker_to_dists.items())

    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        return sum(self.get_dist_weight(ticker) * dist.get_simulated_values(results)
                for ticker, dist in self.ticker_to_dists.items())

    def get_weight_vect(self) -> np.ndarray:
        return np.array([self.get_dist_weight(ticker) for ticker in self.ticker_to_dists], dtype=float)

    def get_expectation_vect(self, t: float = 1) -> np.ndarray:
        return np.array([dist.get_expectation(t) for dist in self.ticker_to_dists.values()], dtype=float)

    def get_covar_mat(self, t: float = 1) -> np.ndarray:
        dists = list(self.ticker_to_dists.values())
        m = len(dists)
        portfolio_covar_mat = np.empty(shape=(m, m), dtype=float)

        for i in range(m):
            portfolio_covar_mat[i, i] = dists[i].get_variance(t)

            for j in range(i + 1, m):
                portfolio_covar_mat[i, j] = dists[i].get_covariance(dists[j], t)
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
    
    def get_plot_range_dist_params(self, t: float = 1) -> tuple[float, float]:
        """ @returns range_dist_params (tuple[float, float]): the mean and standard
                deviation of the plotting range distribution from the first
                asset distribution.
        """
        return list(self.ticker_to_dists.values())[0].get_plot_range_dist_params(t)

if __name__ == "__main__":
    pass