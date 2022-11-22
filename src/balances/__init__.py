import threading
from .balances import Balances

class Portfolio (Balances):
    # Thread-safe balances for access by multiple actors
    def __init__(self):
        Balances.__init__(self)
        self._semaphore = threading.Semaphore(1)

    def add(self, asset_ticker: str, amount: float) -> None:
        with self._semaphore:
            Balances.add(self, asset_ticker, amount)

    def assimilate(self, other: Balances) -> None:
        with self._semaphore:
            Balances.assimilate(self, other)

if __name__ == "__main__":
    pass