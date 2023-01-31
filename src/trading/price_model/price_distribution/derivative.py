import numpy as np

from sympy import Function
from . import AssetPriceDistributionBase
from ..price_model_interface import PriceModelInterface, PriceSimulationResults

class DerivativePriceDistributionBase (AssetPriceDistributionBase):
    def __init__(self, price_model: PriceModelInterface, asset_ticker: str, time_to_expiry: float = None,
        derivative_ticker: str = None, settlement_ticker: str = None) -> None:
        
        AssetPriceDistributionBase.__init__(self, price_model, derivative_ticker)
        self._asset_ticker = asset_ticker
        self.time_to_expiry = time_to_expiry
        self.settlement_ticker = settlement_ticker

    @property
    def asset_ticker(self) -> str:
        return self._asset_ticker

    @property
    def T(self) -> (float | None):
        return self.time_to_expiry

    @property
    def dt(self) -> float:
        # Raises exception where time_to_expiry is not defined.
        return self.T - self.t

    def get_fn(self) -> Function:
        raise NotImplementedError()

    def get_simulated_values(self, results: PriceSimulationResults) -> np.ndarray:
        raise NotImplementedError()

if __name__ == "__main__":
    pass