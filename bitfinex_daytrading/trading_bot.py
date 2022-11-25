import os
import sys
import time
import tensorflow as tf

ROOT_DPATH = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DPATH)

LONG_ENGINE_DPATH = os.path.join(os.path.dirname(__file__), "models",
        "production", "long_trading_engine")
SHORT_ENGINE_DPATH = os.path.join(os.path.dirname(__file__), "models",
        "production", "short_trading_engine")

from src.indicator import FeaturesCompiler
from src.market import MarketBase
from src.market_actor import MarketActorBase
from src.market_listener import MarketListenerBase
from src.advance_order.advance_order_logic import AdvanceOrderLogicInterface

class TradingBot:
    def __init__(self, market_actor: MarketActorBase, market_listener: MarketListenerBase,
        features_compiler: FeaturesCompiler, advance_order_logic: AdvanceOrderLogicInterface,
        long_engine_dpath: str = LONG_ENGINE_DPATH, short_engine_dpath: str = SHORT_ENGINE_DPATH,
        actionable_treshold: float = .8, post_trade_freeze: int = 600):

        self.market_actor = market_actor
        self.market_listener = market_listener
        self.features_compiler = features_compiler

        self.advance_order_logic = advance_order_logic
        self.long_engine_dpath = long_engine_dpath
        self.short_engine_dpath = short_engine_dpath
        self.actionable_treshold = actionable_treshold
        self.post_trade_freeze = post_trade_freeze

        self.long_trading_engine = None
        self.short_trading_engine = None
        self.advance_order = None
        self.frozen_to_time = None
    
    @property
    def market(self) -> MarketBase:
        return self.market_listener.market

    @property
    def trade_position_open(self) -> bool:
        return not (self.advance_order is None)

    def load_trading_engines(self) -> None:
        self.long_trading_engine = tf.keras.models.load_model(self.long_engine_dpath)
        self.short_trading_engine = tf.keras.models.load_model(self.short_engine_dpath)

    def run_events(self):
        # Updates MarketListener
        self.market_listener.update_orderbook()
        self.market_listener.update_tradebook()

        if self.trade_position_open:
            self.advance_order.update()
            
            if self.advance_order.filled: # Reset and freeze bot
                self.frozen_to_time = time.time() + self.post_trade_freeze
                self.advance_order = None
        elif self.frozen_to_time:
            # Bot frozen: no trades allowed
            if self.frozen_to_time >= time.time():
                self.frozen_to_time = None # Unfreeze
        else:
            observation = self.features_compiler.get()
            long_signal = self.long_trading_engine([observation])[0] > self.actionable_treshold
            short_signal = self.short_trading_engine([observation])[0] > self.actionable_treshold

            if long_signal and short_signal:
                return # Do not act on mixed signals

            curr_price = self.market_listener.get_current_price()
            size = 1 if long_signal else -1 # TODO

            position = self.market_actor.open_position(self.market, curr_price, size)
            self.advance_order = self.advance_order_logic.open_advance_order(position)

if __name__ == "__main__":
    pass