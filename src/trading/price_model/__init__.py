import time
import numpy as np

from collections.abc import Iterable
from datetime import datetime
from .price_model_interface import PriceModelInterface
from .price_distribution import AssetPriceDistributionBase
from .price_distribution.option import CallOptionPriceDistributionBase, PutOptionPriceDistributionBase

class PriceModelBase (PriceModelInterface):
    def __init__(self, asset_tickers: Iterable[str], asset_spot_prices: Iterable[float],
        risk_free_rate: float, time_stamp: float = None, base_unit_of_time: int = 31104000) -> None:
        """
        @param asset_tickers (Iterable[str]): the tickers of the assets in the price model universe.
        @param asset_spot_prices (Iterable[float]): the current prices of the assets.
        @param risk_free_rate (str): the borrowing rate of the funding currency.
        @param time_stamp (float, opt): the current time_stamp of the model in seconds.
        @param base_unit_of_time (int, opt): the base time unit in seconds.
                days:   86,400
                months (30 day basis):  2,592,000
                years (360 day basis):  31,104,000
        """
        self.ticker_to_indexes: dict[str, int] = {
            asset_ticker: index for index, asset_ticker in enumerate(asset_tickers)
        }

        self.asset_spot_prices: np.ndarray = np.array(asset_spot_prices, dtype=float)
        self.risk_free_rate = risk_free_rate
        self.base_unit_of_time = base_unit_of_time
        self.time_stamp = time_stamp if time_stamp else time.time()

    # Getters
    def get_spot_price(self, asset_ticker: str) -> float:
        return self.asset_spot_prices[self.ticker_to_indexes[asset_ticker]]
    
    def get_risk_free_rate(self) -> float:
        return self.risk_free_rate

    def get_time_to_expiry(self, expiry_datetime: (float | datetime)) -> float:
        """ @param expiry_datetime (float | datetime): the expiration datetime
                as datetime object or seconds since epoch.
        
        @returns time_to_expiry (float): the time to the expiry datetime, denominated
                in base_unit_of_time.
        """
        if isinstance(expiry_datetime, datetime):
            expiry_datetime = expiry_datetime.timestamp()

        return max(expiry_datetime - self.time_stamp, 0) / self.base_unit_of_time

    def get_day_t(self) -> float:
        """ @returns day_t (float): the time step size for day denominated in
                base_unit_of_time.
        """
        return 86400 / self.base_unit_of_time
    
    def get_month_t(self) -> float:
        """ @returns year_t (float): the time step size for 30-days month denominated in
                base_unit_of_time.
        """
        return 2592000 / self.base_unit_of_time

    def get_year_t(self) -> float:
        """ @returns year_t (float): the time step size for 360-days year denominated in
                base_unit_of_time.
        """
        return 31104000 / self.base_unit_of_time

    # PriceDistribution generators
    def get_asset_price_dist(self, asset_ticker: str) -> AssetPriceDistributionBase:
        raise NotImplementedError()

    def get_call_option_price_dist(self, asset_ticker: str, strike_price: float,\
        time_to_expiry: float, option_ticker: str = None) \
        -> CallOptionPriceDistributionBase:
        raise NotImplementedError()

    def get_put_option_price_dist(self, asset_ticker: str, strike_price: float,\
        time_to_expiry: float, option_ticker: str = None) \
        -> PutOptionPriceDistributionBase:
        raise NotImplementedError()

if __name__ == "__main__":
    pass