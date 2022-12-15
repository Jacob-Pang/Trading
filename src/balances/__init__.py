from .balances import Balances
from threading import Semaphore

class Portfolio (Balances):
    # Thread-safe balances for access by multiple actors
    def __init__(self):
        Balances.__init__(self)
        self._semaphore = Semaphore(1)

    def add_balance(self, ticker: str, size: float) -> None:
        with self._semaphore:
            Balances.add_balance(self, ticker, size)
    
    def add_cfd_balance(self, ticker: str, settlement_ticker: str, size: float, entry_price: float) -> None:
        with self._semaphore:
            Balances.add_cfd_balance(self, ticker, settlement_ticker, size, entry_price)

    def assimilate(self, other: Balances) -> None:
        with self._semaphore:
            Balances.assimilate(self, other)

if __name__ == "__main__":
    pass