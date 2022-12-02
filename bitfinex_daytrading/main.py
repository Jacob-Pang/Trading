import asyncio
import os
import pickle
import sys
import time
import numpy as np
import pandas as pd

from config import *
from bfxapi import Client
from tqdm import tqdm

ROOT_DPATH = os.path.dirname(os.path.dirname(__file__))
DATA_DPATH = os.path.join(os.path.dirname(__file__), "data")
MODELS_DPATH = os.path.join(os.path.dirname(__file__), "models")

sys.path.insert(0, ROOT_DPATH)

from src.market import MarketBase
from src.market.bitfinex import BitfinexSpot
from src.market_actor import MarketActorStub
from src.market_listener import MarketListenerStub
from src.market_listener.bitfinex import BitfinexListener
from src.advance_order.convertible_stop_loss import ConvertibleStopLossLogic
from src.tradebook import Tradebook
from src.trading_bot import TradingBot
from trading_logic import TradingLogic

async def get_candles(bfx: Client, market: MarketBase, epochs: int = 100,
    frame_resolution: str = "1m") -> pd.DataFrame:

    end = int(time.time())
    end -= (end % 60) # Truncate to minutes
    end *= 1000 # Convert to ms

    candles = await asyncio.gather(*[
        bfx.rest.get_public_candles(symbol=market.get_ticker(), start=0,
                end=(end - epoch * 10000 * 60000), limit=10000, tf=frame_resolution)
        for epoch in range(epochs)
    ])

    candles = pd.DataFrame(
        np.concatenate(candles),
        columns=["Timestamp", "Open", "Close", "High", "Low", "Volume"]
    )

    candles["Timestamp"] /= 1000 # Convert from ms to seconds
    candles["Timestamp"] = candles["Timestamp"].astype(int)

    return candles.set_index("Timestamp").sort_index()

def demo():
    market = BitfinexSpot("BTC", "USD")
    market_actor = MarketActorStub(TRANSACT_FEE_RATE, echo_mode=True)
    market_listener = BitfinexListener(market, headless_mode=True)

    # Demo starting with 100 funds
    market_actor.portfolio.add_balance(market.get_funding_currency(), 100)

    # Loading Data Pipeline
    with open(os.path.join(DATA_DPATH, "data_pipeline.pickle"), "rb") as file:
        data_pipeline = pickle.load(file)
        
        candle_buffers = data_pipeline.get("candle_buffers")
        features_compiler = data_pipeline.get("features_compiler")

    candles = asyncio.run(get_candles(Client(), market, epochs=1))
    assert candles.values.shape[0] > 0

    # Updating CandleBuffer
    tradebook = Tradebook(10) # To facilitate update of orderbook

    for timestamp, data in tqdm(list(candles.iterrows())):
        update_timestamp = timestamp - 1 # The passed timestamp denotes the end of time frame
        tradebook.append_trade(update_timestamp, (data.get("Open") + data.get("Close")) / 2,
                data.get("Volume"))
        
        for candle_buffer in candle_buffers.values():
            candle_buffer.update(update_timestamp, data.get("Open"), tradebook)
            candle_buffer.update(update_timestamp, data.get("High"), tradebook)
            candle_buffer.update(update_timestamp, data.get("Low"), tradebook)
            candle_buffer.update(update_timestamp, data.get("Close"), tradebook)

    trading_logic = TradingLogic(market_actor, market_listener, features_compiler)

    advance_order_logic = ConvertibleStopLossLogic(market_actor, market_listener,
            STOP_LOSS_RATE, trailing_rate=TRAILING_RATE, offset_as_rate=True,
            use_orderbook=False)

    # Making TradingBot
    trading_bot = TradingBot(market_actor, market_listener, trading_logic, advance_order_logic,
            trading_cooldown=TRADING_COOLDOWN, trading_logic_update_intv=86400)

    trading_bot.subscribe_to_listener()
    heartbeat_interval = 60 * 60
    heartbeat_time = time.time() + heartbeat_interval

    while True: # TODO: Require some command interface
        trading_bot.do_events()
        time.sleep(1)

        if time.time() > heartbeat_time:
            print(f"TradingBot Loop Heartbeat.")
            heartbeat_time += heartbeat_interval
            # estart and subscribe MarketListener
            market_listener.subscribe()

    market_listener.close()

if __name__ == "__main__":
    # asyncio for windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    demo()
