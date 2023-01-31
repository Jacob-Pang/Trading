import numpy as np
from .. import Portfolio

class PortfolioOptimizerInterface:
    def get_optimized_weights(self, portfolio: Portfolio) -> np.ndarray:
        raise NotImplementedError()

    def apply_weights(self, portfolio: Portfolio, weights: np.ndarray) -> None:
        entry_cost = portfolio.get_entry_cost()

        for ticker, weight in zip(portfolio.ticker_to_balances.keys(), weights):
            balance = portfolio.ticker_to_balances[ticker]
            balance.size = (weight * entry_cost) / balance.entry_price

if __name__ == "__main__":
    pass