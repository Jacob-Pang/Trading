from .derivative import DerivativePriceDistributionBase
from ..price_model_interface import PriceModelInterface

class OptionPriceDistributionBase (DerivativePriceDistributionBase):
    def __init__(self, price_model: PriceModelInterface, asset_ticker: str,
        strike_price: float, time_to_expiry: float, option_ticker: str = None) -> None:
        
        DerivativePriceDistributionBase.__init__(self, price_model, asset_ticker,
                time_to_expiry, option_ticker)

        self.strike_price = strike_price
        assert self.dt >= 0

    @property
    def K(self) -> float:
        return self.strike_price

class CallOptionPriceDistributionBase (OptionPriceDistributionBase):
    pass

class PutOptionPriceDistributionBase (OptionPriceDistributionBase):
    pass

if __name__ == "__main__":
    pass