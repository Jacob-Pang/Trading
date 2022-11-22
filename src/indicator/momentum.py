from . import IndicatorBase
from ..candle_buffer import CandleBuffer
from talib import abstract

class MomentumIndicatorBase (IndicatorBase):
    # Momentum Indicator for TaLib momentum indicators.
    momentum_indicator = None

    def __init__(self, candle_buffer: CandleBuffer) -> None:
        assert candle_buffer.get_capacity() >= 50 # mim candles required.

        IndicatorBase.__init__(self)
        self.candle_buffer = candle_buffer
        self.momentum_funct = getattr(abstract, self.momentum_indicator)

    def __reduce__(self) -> tuple:
        return (self.__class__, (self.candle_buffer,))

# TaLib momentum classes
class ADX (MomentumIndicatorBase):
    momentum_indicator = "ADX"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(30),
            self.candle_buffer.get_low_data(30),
            self.candle_buffer.get_close_data(30)
        )[-1])

class ADXR (MomentumIndicatorBase):
    momentum_indicator = "ADXR"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(50),
            self.candle_buffer.get_low_data(50),
            self.candle_buffer.get_close_data(50)
        )[-1])

class APO (MomentumIndicatorBase):
    momentum_indicator = "APO"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(30))[-1])

class AROON (MomentumIndicatorBase):
    momentum_indicator = "AROON"

    def get_num_features(self) -> int:
        return 2

    def update(self) -> float:
        aroon_down, aroon_up = self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20)
        )

        self.set(0, aroon_down[-1])
        self.set(1, aroon_up[-1])

class AROONOSC (MomentumIndicatorBase):
    momentum_indicator = "AROONOSC"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20)
        )[-1])

class BOP (MomentumIndicatorBase):
    momentum_indicator = "BOP"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_open_data(20),
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )[-1])

class CCI (MomentumIndicatorBase):
    momentum_indicator = "CCI"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )[-1])

class CMO (MomentumIndicatorBase):
    momentum_indicator = "CMO"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class DX (MomentumIndicatorBase):
    momentum_indicator = "DX"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )[-1])

class MACD (MomentumIndicatorBase):
    momentum_indicator = "MACD"

    def get_num_features(self) -> int:
        return 3

    def update(self) -> float:
        macd, macdsignal, macdhist = self.momentum_funct(self.candle_buffer.get_close_data(40))
        self.set(0, macd[-1])
        self.set(1, macdsignal[-1])
        self.set(2, macdhist[-1])

class MFI (MomentumIndicatorBase):
    momentum_indicator = "MFI"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20),
            self.candle_buffer.get_volume_data(20)
        )[-1])

class MINUS_DI (MomentumIndicatorBase):
    momentum_indicator = "MINUS_DI"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )[-1])

class MINUS_DM (MomentumIndicatorBase):
    momentum_indicator = "MINUS_DM"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20)
        )[-1])

class MOM (MomentumIndicatorBase):
    momentum_indicator = "MOM"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class PLUS_DI (MomentumIndicatorBase):
    momentum_indicator = "PLUS_DI"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )[-1])

class PLUS_DM (MomentumIndicatorBase):
    momentum_indicator = "PLUS_DM"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20)
        )[-1])

class PPO (MomentumIndicatorBase):
    momentum_indicator = "PPO"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class ROC (MomentumIndicatorBase):
    momentum_indicator = "ROC"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class ROCP (MomentumIndicatorBase):
    momentum_indicator = "ROCP"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class ROCR (MomentumIndicatorBase):
    momentum_indicator = "ROCR"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class RSI (MomentumIndicatorBase):
    momentum_indicator = "RSI"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class STOCH (MomentumIndicatorBase):
    momentum_indicator = "STOCH"

    def get_num_features(self) -> int:
        return 2

    def update(self) -> float:
        slowk, slowd = self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )

        self.set(0, slowk[-1])
        self.set(1, slowd[-1])

class STOCHF (MomentumIndicatorBase):
    momentum_indicator = "STOCHF"

    def get_num_features(self) -> int:
        return 2

    def update(self) -> float:
        fastk, fastd = self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )

        self.set(0, fastk[-1])
        self.set(1, fastd[-1])

class STOCHRSI (MomentumIndicatorBase):
    momentum_indicator = "RSI"

    def get_num_features(self) -> int:
        return 2

    def update(self) -> float:
        fastk, fastd = self.momentum_funct(self.candle_buffer.get_close_data(20))

        self.set(0, fastk[-1])
        self.set(1, fastd[-1])

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(20))[-1])

class TRIX (MomentumIndicatorBase):
    momentum_indicator = "TRIX"

    def update(self) -> float:
        self.set(0, self.momentum_funct(self.candle_buffer.get_close_data(40))[-1])

class ULTOSC (MomentumIndicatorBase):
    momentum_indicator = "ULTOSC"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(30),
            self.candle_buffer.get_low_data(30),
            self.candle_buffer.get_close_data(30)
        )[-1])

class WILLR (MomentumIndicatorBase):
    momentum_indicator = "WILLR"

    def update(self) -> float:
        self.set(0, self.momentum_funct(
            self.candle_buffer.get_high_data(20),
            self.candle_buffer.get_low_data(20),
            self.candle_buffer.get_close_data(20)
        )[-1])

MOMENTUM_INDICATOR_LIST = [ADX, ADXR, APO, AROON, AROONOSC, BOP, CCI, CMO, DX, MACD, MFI, MINUS_DI, MINUS_DM, MOM, PLUS_DI, PLUS_DM, PPO, ROC, ROCP, ROCR, RSI, STOCH, STOCHF, STOCHRSI, TRIX, ULTOSC, WILLR]

def get_momentum_indicator_suite(candle_buffer: CandleBuffer) -> list[MomentumIndicatorBase]:
    # Returns the full suite of MomentumIndicators
    return [
        momentum_indicator(candle_buffer)
        for momentum_indicator in MOMENTUM_INDICATOR_LIST
    ]

if __name__ == "__main__":
    pass