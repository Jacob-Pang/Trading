import numpy as np

from sympy import Function, Symbol
from ..distribution import AssetDistributionBase, PortfolioDistributionBase
from ..price_model_interface import PriceModelInterface, PriceSimulationResults

class PriceDistributionInterface:
    def __init__(self, price_model: PriceModelInterface) -> None:
        """
        @param price_model (PriceModelInterface): the parent pricing model.
        @param ticker (str): the identifying ticker, generates an UUID by default.
        """
        self.price_model = price_model

    @property
    def t(self) -> float:
        return self.price_model.get_time_step_size()

    @property
    def r(self) -> float:
        return self.price_model.get_risk_free_rate()

class AssetPriceDistributionBase (AssetDistributionBase, PriceDistributionInterface):
    def __init__(self, price_model: PriceModelInterface, ticker: str = None) -> None:
        """
        @param price_model (PriceModelInterface): the parent pricing model.
        @param ticker (str): the identifying ticker, generates an UUID by default.
        """
        AssetDistributionBase.__init__(self, ticker)
        PriceDistributionInterface.__init__(self, price_model)

    @property
    def s0(self) -> float:
        return self.price_model.get_spot_price(self.asset_ticker)
    
    @property
    def st(self) -> Symbol:
        return Symbol(self.asset_ticker)

    def get_fn(self) -> Function:
        return self.st

    def get_density_fn(self) -> Function:
        return self.price_model.get_asset_density_fn(self.asset_ticker)

    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        """ @returns simulated_prices (np.ndarray): the prices (time_steps x paths) in the results
                corresponding to the @param asset_ticker.
        """
        return results.get_simulated_prices(self.asset_ticker)

    def get_plot_xvar(self) -> Symbol:
        return self.st

    def get_plot_fn_label(self) -> str:
        return f"{self.ticker}_price"

class PortfolioPriceDistribution (PortfolioDistributionBase, PriceDistributionInterface):
    ticker_to_dists: dict[str, AssetPriceDistributionBase]

    def __init__(self, price_model: PriceModelInterface) -> None:
        """
        @param price_model (PriceModelInterface): the parent pricing model.
        @param ticker (str): the identifying ticker, generates an UUID by default.
        """
        PortfolioDistributionBase.__init__(self)
        PriceDistributionInterface.__init__(self, price_model)
    
    def add(self, price_dist: AssetPriceDistributionBase, size: float) -> None:
        assert isinstance(price_dist, AssetPriceDistributionBase)
        return PortfolioDistributionBase.add(self, price_dist, size)

    def get_dist_weight(self, ticker: str) -> float:
        return self.ticker_to_sizes[ticker]

    def get_density_fn(self) -> Function:
        return self.price_model.get_joint_density_fn({
            dist.asset_ticker for dist in self.ticker_to_dists.values()
        })

    def get_plot_fn_label(self) -> str:
        return f"portfolio_price"

if __name__ == "__main__":
    pass