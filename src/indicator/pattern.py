from . import IndicatorBase
from ..candle_buffer import CandleBuffer
from talib import abstract

PATTERN_LIST_STR = """
CDL2CROWS            Two Crows
CDL3BLACKCROWS       Three Black Crows
CDL3INSIDE           Three Inside Up/Down
CDL3LINESTRIKE       Three-Line Strike
CDL3OUTSIDE          Three Outside Up/Down
CDL3STARSINSOUTH     Three Stars In The South
CDL3WHITESOLDIERS    Three Advancing White Soldiers
CDLABANDONEDBABY     Abandoned Baby
CDLADVANCEBLOCK      Advance Block
CDLBELTHOLD          Belt-hold
CDLBREAKAWAY         Breakaway
CDLCLOSINGMARUBOZU   Closing Marubozu
CDLCONCEALBABYSWALL  Concealing Baby Swallow
CDLCOUNTERATTACK     Counterattack
CDLDARKCLOUDCOVER    Dark Cloud Cover
CDLDOJI              Doji
CDLDOJISTAR          Doji Star
CDLDRAGONFLYDOJI     Dragonfly Doji
CDLENGULFING         Engulfing Pattern
CDLEVENINGDOJISTAR   Evening Doji Star
CDLEVENINGSTAR       Evening Star
CDLGAPSIDESIDEWHITE  Up/Down-gap side-by-side white lines
CDLGRAVESTONEDOJI    Gravestone Doji
CDLHAMMER            Hammer
CDLHANGINGMAN        Hanging Man
CDLHARAMI            Harami Pattern
CDLHARAMICROSS       Harami Cross Pattern
CDLHIGHWAVE          High-Wave Candle
CDLHIKKAKE           Hikkake Pattern
CDLHIKKAKEMOD        Modified Hikkake Pattern
CDLHOMINGPIGEON      Homing Pigeon
CDLIDENTICAL3CROWS   Identical Three Crows
CDLINNECK            In-Neck Pattern
CDLINVERTEDHAMMER    Inverted Hammer
CDLKICKING           Kicking
CDLKICKINGBYLENGTH   Kicking - bull/bear determined by the longer marubozu
CDLLADDERBOTTOM      Ladder Bottom
CDLLONGLEGGEDDOJI    Long Legged Doji
CDLLONGLINE          Long Line Candle
CDLMARUBOZU          Marubozu
CDLMATCHINGLOW       Matching Low
CDLMATHOLD           Mat Hold
CDLMORNINGDOJISTAR   Morning Doji Star
CDLMORNINGSTAR       Morning Star
CDLONNECK            On-Neck Pattern
CDLPIERCING          Piercing Pattern
CDLRICKSHAWMAN       Rickshaw Man
CDLRISEFALL3METHODS  Rising/Falling Three Methods
CDLSEPARATINGLINES   Separating Lines
CDLSHOOTINGSTAR      Shooting Star
CDLSHORTLINE         Short Line Candle
CDLSPINNINGTOP       Spinning Top
CDLSTALLEDPATTERN    Stalled Pattern
CDLSTICKSANDWICH     Stick Sandwich
CDLTAKURI            Takuri (Dragonfly Doji with very long lower shadow)
CDLTASUKIGAP         Tasuki Gap
CDLTHRUSTING         Thrusting Pattern
CDLTRISTAR           Tristar Pattern
CDLUNIQUE3RIVER      Unique 3 River
CDLUPSIDEGAP2CROWS   Upside Gap Two Crows
CDLXSIDEGAP3METHODS  Upside/Downside Gap Three Methods
"""

PATTERN_LIST = [
    pattern.split(' ', maxsplit=1)[0] # Drop description
    for pattern in PATTERN_LIST_STR.split('\n')[1:-1]
]

PATTERN_FUNCT_MAP = {
    pattern : getattr(abstract, pattern)
    for pattern in PATTERN_LIST
}

class PatternIndicator (IndicatorBase):
    # Pattern Indicator for TaLib patterns.
    # Observation values range from [-2, 2].
    def __init__(self, pattern: str, candle_buffer: CandleBuffer) -> None:
        """ @param pattern (str): The pattern name from PATTERN_LIST.
            @param candles_buffer (CandlesBuffer): Reads OHLCV from this buffer to generate observations.
        """
        assert candle_buffer.get_capacity() > 30 # minimum candles required.

        IndicatorBase.__init__(self)
        self.candle_buffer = candle_buffer
        self.pattern = pattern
        self.pattern_funct = PATTERN_FUNCT_MAP.get(pattern)
        self.curr_obseration = 0
    
    def update(self) -> None:
        self.set(0, self.pattern_funct(
            self.candle_buffer.get_open_data(30),
            self.candle_buffer.get_high_data(30),
            self.candle_buffer.get_low_data(30),
            self.candle_buffer.get_close_data(30)
        )[-1] / 100)

    def __reduce__(self) -> tuple:
        return (self.__class__, (self.pattern, self.candle_buffer,))

def get_pattern_indicator_suite(candle_buffer: CandleBuffer) -> list[PatternIndicator]:
    # Returns the full suite of PatternIndicators.
    return [
        PatternIndicator(pattern, candle_buffer)
        for pattern in PATTERN_LIST
    ]

if __name__ == "__main__":
    pass