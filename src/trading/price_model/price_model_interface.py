import numpy as np

from sympy import Function

class PriceSimulationResults:
    def __init__(self, tickers_to_index: dict[str, int], results: np.ndarray, t: float) -> None:
        """ Container for asset prices generated from @method PriceModelInterface.simulate_prices
        @param asset_tickers (dict[str, int]): the mapping of asset asset_tickers to index.
        @param results (np.ndarray): the generated prices (m_assets x time_steps x paths).
        @param t (float): the size of the time step.
        """
        self.asset_tickers: dict[str, int] = tickers_to_index
        self.results: np.ndarray = results
        self.t = t

    def get_simulated_prices(self, asset_ticker: str) -> np.ndarray:
        """ @returns simulated_prices (np.ndarray): the prices (time_steps x paths) in the results
                corresponding to the @param asset_ticker.
        """
        index = self.asset_tickers[asset_ticker]

        return self.results[index]

class PriceModelInterface:
    # Getters    
    def get_risk_free_rate(self) -> float:
        raise NotImplementedError()

    def get_spot_price(self, asset_ticker: str) -> float:
        raise NotImplementedError()

    def get_asset_density_fn(self, asset_ticker: str, t: float = 1) -> Function:
        raise NotImplementedError()

    def get_joint_density_fn(self, asset_tickers: set[str], t: float = 1) -> Function:
        raise NotImplementedError()

    # Simulation methods
    def simulate_prices(self, paths: int, time_steps: int, t: float = 1) \
        -> PriceSimulationResults:
        raise NotImplementedError()

if __name__ == "__main__":
    pass