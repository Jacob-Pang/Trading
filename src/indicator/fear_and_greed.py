import requests
import time
import numpy as np

from . import IndicatorBase

class CryptoFearAndGreed (IndicatorBase):
    # Observation values range:
    #   Unscaled: [0, 100]
    #   Rescaled: [-1, 1]
    @staticmethod
    def standardized_scale(observation: (float| np.ndarray)) -> (float| np.ndarray):
        return (observation - 50) / 50
    
    @staticmethod
    def get_hist_data(max_records: int = 5000, apply_scaling: bool = True) -> tuple[np.ndarray, np.ndarray]:
        # Returns (timestamps, observations)
        hist_data = requests.get(f"https://api.alternative.me/fng/?limit={max_records}") \
                .json().get("data")
        
        records = len(hist_data)
        timestamps = np.empty(shape=(records,), dtype=int)
        observations = np.empty(shape=(records,), dtype=float)

        for t, record in enumerate(reversed(hist_data)):
            timestamps[t] = record.get("timestamp")
            observations[t] = record.get("value")

        if apply_scaling:
            observations = CryptoFearAndGreed.standardized_scale(observations)

        return timestamps, observations

    def __init__(self, apply_scaling: bool = True) -> None:
        IndicatorBase.__init__(self, "crypto_fear_and_greed")
        self.apply_scaling = apply_scaling
        self.next_update_time = time.time() - 1

    def update(self) -> None:
        if self.next_update_time < time.time():
            # Update due
            data = requests.get(f"https://api.alternative.me/fng/?limit=1") \
                    .json().get("data")[0]

            time_to_update = data.get("time_until_update")
            self.next_update_time = int(time.time() + int(time_to_update))
            current_observation = float(data.get("value"))

            if self.apply_scaling:
                current_observation = CryptoFearAndGreed.standardized_scale(current_observation)

            self.set(0, current_observation)

    def __reduce__(self) -> tuple:
        return (self.__class__, (self.apply_scaling,))

if __name__ == "__main__":
    pass
