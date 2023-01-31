from copy import copy
from threading import Semaphore
from .balance import AssetBalance
from ..price_model import PriceModelBase
from ..price_model.price_distribution import PortfolioPriceDistribution
from ..price_model.return_distribution import PortfolioReturnDistribution

class Portfolio:
    def __init__(self) -> None:
        self.ticker_to_balances = dict[str, AssetBalance]()
        self._sem = Semaphore(1)

    # Getters
    def get_entry_cost(self) -> float:
        return sum(balance.get_entry_cost() for balance in self.ticker_to_balances.values())

    def get_balance(self, ticker: str) -> AssetBalance:
        return self.ticker_to_balances.get(ticker)

    def get_size(self, ticker: str) -> float:
        return self.ticker_to_balances.get(ticker).size \
                if ticker in self.ticker_to_balances else 0

    def get_value(self, ticker_to_price: dict[str, float]) -> float:
        portfolio_value = 0

        for balance in self.ticker_to_balances.values():
            if balance.ticker in ticker_to_price:
                portfolio_value += balance.size * ticker_to_price.get(balance.ticker)

        return portfolio_value

    def get_price_dist(self, price_model: PriceModelBase) -> PortfolioPriceDistribution:
        port_price_dist = PortfolioPriceDistribution(price_model)

        for balance in self.ticker_to_balances.values():
            port_price_dist.add(balance.get_price_dist(price_model), balance.size)

        return port_price_dist

    def get_ret_dist(self, price_model: PriceModelBase) -> PortfolioReturnDistribution:
        port_ret_dist = PortfolioReturnDistribution(price_model)

        for balance in self.ticker_to_balances.values():
            port_ret_dist.add(balance.get_ret_dist(price_model), balance.size)

        return port_ret_dist

    def get_contra_portfolio(self) -> "Portfolio":
        contra_port = Portfolio()

        for balance in self.ticker_to_balances.values():
            contra_balance = copy(balance)
            contra_balance.size = -balance.size

            contra_port.add(contra_balance)

        return contra_port

    def __repr__(self) -> str:
        return self.ticker_to_balances.__repr__()

    # Mutators
    def add(self, balance: "AssetBalance") -> None:
        with self._sem:
            if balance.ticker in self.ticker_to_balances:
                self.ticker_to_balances.get(balance.ticker).assimilate(balance)
            else: # Reference to balance object maintained.
                self.ticker_to_balances[balance.ticker] = balance

    def remove(self, ticker: str) -> None:
        if ticker in self.ticker_to_balances:
            self.ticker_to_balances.pop(ticker)

    def assimilate(self, other: "Portfolio") -> None:
        with self._sem:
            for balance in other.ticker_to_balances.values():
                if balance.ticker in self.ticker_to_balances:
                    self.ticker_to_balances.get(balance.ticker).assimilate(balance)
                else:
                    self.ticker_to_balances[balance.ticker] = copy(balance)

if __name__ == "__main__":
    pass