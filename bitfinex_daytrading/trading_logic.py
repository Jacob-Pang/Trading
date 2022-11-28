import os
import pickle
import sys
import numpy as np
import tensorflow as tf
from tensorflow.python import keras
from tensorflow.python.keras.models import load_model

ROOT_DPATH = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DPATH)

TRADING_ENGINE_DPATH = os.path.join(os.path.dirname(__file__), "models", "production")
SHORT_ENGINE_DPATH = os.path.join(os.path.dirname(__file__), "models",
        "production", "short_trading_engine")

from src.indicator import FeaturesCompiler
from src.market import MarketBase
from src.market_actor import MarketActorBase
from src.market_listener import MarketListenerBase
from src.trading_logic import TradingLogicInterface

class TradingLogic (TradingLogicInterface):
    def __init__(self, market_actor: MarketActorBase, market_listener: MarketListenerBase,
        features_compiler: FeaturesCompiler, trading_engine_dpath: str = TRADING_ENGINE_DPATH,
        actionable_probability: float = .8, open_position_ratio: float = .5):

        self.market_actor = market_actor
        self.market_listener = market_listener
        self.features_compiler = features_compiler
        self.trading_engine_dpath = trading_engine_dpath
        self.actionable_probability = actionable_probability
        self.open_position_ratio = open_position_ratio

        self.long_trading_engine = None
        self.short_trading_engine = None
        self.long_scaler = None
        self.short_scaler = None
    
    @property
    def market(self) -> MarketBase:
        return self.market_listener.market

    def update(self) -> None:
        # Reload the tensorflow models
        self.long_trading_engine = load_model(os.path.join(self.trading_engine_dpath,
                "long_trading_engine"))
        self.short_trading_engine = tf.keras.models.load_model(os.path.join(self.trading_engine_dpath,
                "short_trading_engine"))
        
        with open(os.path.join(self.trading_engine_dpath, "long_scaler.pickle"), "rb") as file:
            self.long_scaler = pickle.load(file)

        with open(os.path.join(self.trading_engine_dpath, "short_scaler.pickle"), "rb") as file:
            self.short_scaler = pickle.load(file)

    def get_open_trade(self) -> tuple[float, float]:
        observation = self.features_compiler.get()
        observation = np.reshape(observation, (1, observation.shape[0]))

        long_trading_signal = self.long_trading_engine(self.long_scaler.transform(observation))[0] \
                > self.actionable_probability
        short_trading_signal = self.short_trading_engine(self.short_scaler.transform(observation))[0] \
                > self.actionable_probability

        if (long_trading_signal == short_trading_signal):
            # Does not act on mixed trading signals or both signals are false.
            return 0, 0
        
        # naive tradeable funds computation
        tradeable_funds = self.market_actor.portfolio.get_size(self.market.get_funding_currency()) \
                * self.open_position_ratio

        orderbook = self.market_listener.get_orderbook()

        # Note that trading size is limited by orderbook entries here
        return orderbook.get_market_ask(tradeable_funds) if long_trading_signal else \
                orderbook.get_market_bid(tradeable_funds)

if __name__ == "__main__":
    pass