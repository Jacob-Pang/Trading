import time
import numpy as np

from .stub import MarketListenerStub

class GBMMarketListener (MarketListenerStub):
    def __init__(self, current_price: float, drift: float, volatility: float,
        tradebook_capacity: int = 100, max_orderbook_entries: int = None,
        base_unit_of_time: int = 31104000):

        MarketListenerStub.__init__(self, tradebook_capacity, max_orderbook_entries)
        self.current_price = current_price
        self.drift = drift
        self.volatility = volatility
        self.timestamp = time.time()
        self.base_unit_of_time = base_unit_of_time

    # Setter
    def update(self) -> None:
        with self._update_semaphore:
            current_timestamp = time.time()
            dt = (current_timestamp - self.timestamp) / self.base_unit_of_time
            self.current_price = np.random.lognormal(
                mean=np.log(self.current_price) + (self.drift - self.volatility ** 2 / 2) * dt,
                sigma=self.volatility * np.sqrt(dt)
            )

if __name__ == "__main__":
    pass