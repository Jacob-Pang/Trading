import time

from .market import MarketBase
from .market_actor import MarketActorBase
from .market_listener import MarketListenerBase
from .trading_logic import TradingLogicInterface
from .advance_order.advance_order_logic import AdvanceOrderLogicInterface
from pyutils.events import wait_for

class TradingBot:
    def __init__(self, market_actor: MarketActorBase, market_listener: MarketListenerBase,
        trading_logic: TradingLogicInterface, advance_order_logic: AdvanceOrderLogicInterface,
        trading_cooldown: float = 300, trading_logic_update_intv: float = 300, reconnect_attempts:
        int = 200, update_orderbook_entries: int = 5):
        """
        @param market_actor (MarketActorBase): Uses the actor to open and close positions.
        @param market_listener (MarketListenerBase): Updates the listener on every event.
        @param trading_logic (TradingLogicInterface): Uses the trading_logic to determine the
                price and size to open a new position.
        @param advance_order_logic (AdvanceOrderLogicInterface): Uses the advance_order_logic
                to open an advance_order post opening of a new position.
        @param trading_cooldown (float): The downtime post-closing of position during which
                no new positions can be opened.
        @param trading_logic_update_intv (float): The interval between each update of the
                trading_logic engine; note that an update is performed on the first event.
        @param reconnect_attempts (int): The number of attempts to try reconnecting in the
                situation where the market_listener connection is lost.
        @param update_orderbook_entries (int): The number of orderbook entries to update for
                on every update_orderbook event.
        """
        self.market_actor = market_actor
        self.market_listener = market_listener
        self.trading_logic = trading_logic
        self.advance_order_logic = advance_order_logic
        self.trading_cooldown = trading_cooldown
        self.trading_logic_update_intv = trading_logic_update_intv
        self.reconnect_attempts = reconnect_attempts
        self.update_orderbook_entries = update_orderbook_entries

        self.advance_order = None # Container for the current position
        self.active_time = 0
        self.update_trading_logic_time = 0

    @property
    def market(self) -> MarketBase:
        return self.market_listener.market

    def has_existing_position(self) -> bool:
        return not (self.advance_order is None)

    def subscribe_to_listener(self) -> None:
        self.market_listener.subscribe()

        while not self.market_listener.ready():
            time.sleep(.2) # Busy waiting

    def update_trading_logic(self) -> None:
        self.trading_logic.update()
        self.update_trading_logic_time = time.time() + self.trading_logic_update_intv

    def update_market_listener(self) -> None:
        try:
            self.market_listener.update_orderbook(self.update_orderbook_entries)
            self.market_listener.update_tradebook()
            return
        except:
            pass
        
        for _ in range(self.reconnect_attempts - 1):
            try:
                self.subscribe_to_listener()
                self.market_listener.update_orderbook(self.update_orderbook_entries)
                self.market_listener.update_tradebook()
                return
            except:
                pass

        # Final attempt: exceptions thrown
        self.subscribe_to_listener()
        self.market_listener.update_orderbook(self.update_orderbook_entries)
        self.market_listener.update_tradebook()

    def do_events(self) -> None:
        if not self.has_existing_position() and time.time() > self.update_trading_logic_time:
            # Does not perform update while an active position is being managed.
            self.update_trading_logic()

        self.update_market_listener()

        if self.has_existing_position():
            self.advance_order.update()

            if self.advance_order.filled: # Activate trading_cooldown
                self.active_time = time.time() + self.trading_cooldown
                self.advance_order = None

        elif self.active_time <= time.time():
            trade_price, trade_size = self.trading_logic.get_open_trade()

            if not trade_size:
                return
    
            order = self.market_actor.place_open_order(self.market, trade_price, trade_size)
            wait_for(order.has_filled, timeout=60)
            self.advance_order = self.advance_order_logic.open_advance_order(order.filled_position)

if __name__ == "__main__":
    pass