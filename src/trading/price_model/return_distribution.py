import numpy as np

from sympy import Function, Symbol
from .price_distribution import AssetPriceDistributionBase
from .price_model_interface import PriceModelInterface, PriceSimulationResults
from .temporal_distribution import TemporalDistributionBase, AssetTemporalDistributionBase, \
        PortfolioTemporalDistributionBase

class ReturnDistributionInterface:
    def __init__(self, price_model: PriceModelInterface, entry_price: float) -> None:
        self.price_model = price_model
        self.entry_price = entry_price

class AssetReturnDistribution (AssetTemporalDistributionBase, ReturnDistributionInterface):
    def __init__(self, price_dist: AssetPriceDistributionBase, entry_price: float) -> None:
        AssetTemporalDistributionBase.__init__(self, f"{price_dist.ticker}+R")
        ReturnDistributionInterface.__init__(self, price_dist.price_model, entry_price)
        self.price_dist = price_dist

    @property
    def asset_ticker(self) -> str:
        return self.price_dist.asset_ticker

    def get_fn(self, t: float = 1) -> Function:
        return self.price_dist.get_fn(t) / self.entry_price - 1

    def get_density_fn(self, t: float = 1) -> Function:
        return self.price_dist.get_density_fn(t)

    def get_expectation(self, t: float = 1) -> float:
        return self.price_dist.get_expectation(t) / self.entry_price - 1
    
    def get_variance(self, t: float = 1) -> float:
        return self.price_dist.get_variance(t) / (self.entry_price ** 2)
    
    def get_covariance(self, other: TemporalDistributionBase, t: float = 1) -> float:
        if isinstance(other, AssetReturnDistribution):
            return self.price_dist.get_covariance(other.price_dist, t) \
                    / (self.entry_price * other.entry_price)
        elif isinstance(other, AssetPriceDistributionBase):
            return self.price_dist.get_covariance(other, t) / self.entry_price
        
        # PortfolioDistribution
        return other.get_covariance(self, t)

    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        return self.price_dist.get_simulated_values(results) / self.entry_price - 1

    def get_plot_xvar(self) -> Symbol:
        return self.price_dist.get_plot_xvar()

    def get_plot_range_dist_params(self, t: float = 1) -> tuple[float, float]:
        return self.price_dist.get_plot_range_dist_params(t)

    def get_plot_fn_label(self) -> str:
        return f"{self.price_dist.ticker}_return"

class PortfolioReturnDistribution (PortfolioTemporalDistributionBase, ReturnDistributionInterface):
    ticker_to_dists: dict[str, AssetReturnDistribution]

    def __init__(self, price_model: PriceModelInterface) -> None:
        PortfolioTemporalDistributionBase.__init__(self)
        ReturnDistributionInterface.__init__(self, price_model, 0)
    
    def add(self, dist: AssetReturnDistribution, size: float) -> None:
        assert isinstance(dist, AssetReturnDistribution)
        self.entry_price += size * dist.entry_price

        return PortfolioTemporalDistributionBase.add(self, dist, size)

    def get_dist_weight(self, ticker: str) -> float:
        return self.ticker_to_sizes[ticker] * self.ticker_to_dists[ticker].entry_price \
                / self.entry_price

    def get_density_fn(self, t: float = 1) -> Function:
        return self.price_model.get_joint_density_fn({
            dist.asset_ticker for dist in self.ticker_to_dists.values()
        })

    def get_plot_fn_label(self) -> str:
        return "portfolio_return"

if __name__ == "__main__":
    pass