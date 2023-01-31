from .. import MarketListenerBase
from ...listener.rpa import RPAListenerBase

from lxml import etree
from pyutils.websurfer import XPathIdentifier
from pyutils.websurfer.rpa import RPAWebSurfer
from pyutils.websurfer.rpa.manager import RPAManager
from pyutils.websurfer.rpa.manager import rpa_manager

class RPAMarketListenerBase (RPAListenerBase, MarketListenerBase):
    # MarketListener using RPA
    # xpaths to be overriden
    curr_price_xpath = None
    bid_orderbook_size_xpath  = None
    bid_orderbook_price_xpath = None
    ask_orderbook_size_xpath  = None
    ask_orderbook_price_xpath = None
    trades_timestamp_xpath = None
    trades_price_xpath = None
    trades_size_xpath  = None
    
    # RPAMarketListener methods
    def __init__(self, tradebook_capacity: int = 100, max_orderbook_entries: int = None,
        visual_automation: bool = False, chrome_browser: bool = True, headless_mode: bool = False,
        turbo_mode: bool = False, rpa_manager: RPAManager = rpa_manager, rpa_instance_id: int = None,
        chrome_scan_period: int = 0, sleeping_period: int = 0, engine_scan_period: int = 0,
        incognito_mode: bool = False):

        RPAListenerBase.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                rpa_manager, rpa_instance_id, chrome_scan_period, sleeping_period,
                engine_scan_period, incognito_mode)

        MarketListenerBase.__init__(self, tradebook_capacity, max_orderbook_entries)
        
    # Abstract methods
    def convert_to_float(self, num_text: str) -> float:
        # data cleaning method that can be overriden to optimize efficiency
        return float(num_text.replace(' ', '').replace(',', ''))

    def convert_to_timestamp(self, timestamp_text: str) -> int:
        raise NotImplementedError()

    # Getters
    def get(self) -> float:
        return MarketListenerBase.get(self)

    def get_current_price(self) -> float:
        return self.convert_to_float(self.get_text(XPathIdentifier(self.curr_price_xpath)))

    def get_current_bid(self) -> tuple[float, float]:
        bid_price = self.convert_to_float(self.get_text(XPathIdentifier(self.bid_orderbook_price_xpath)))
        bid_size  = self.convert_to_float(self.get_text(XPathIdentifier(self.bid_orderbook_size_xpath)))
        
        return bid_price, bid_size

    def get_current_ask(self) -> tuple[float, float]:
        ask_price = self.convert_to_float(self.get_text(XPathIdentifier(self.ask_orderbook_price_xpath)))
        ask_size  = self.convert_to_float(self.get_text(XPathIdentifier(self.ask_orderbook_size_xpath)))
        
        return ask_price, ask_size
    
    # Mutators
    def update(self) -> None:
        # Updates both orderbook and tradebook
        with self._update_semaphore:
            self._tree: etree._ElementTree = etree.HTML(self.page_source())
            self.update_orderbook()
            self.update_tradebook()
            self._tree = None

    def update_orderbook(self, tree = None) -> None:
        tree: etree._ElementTree = self._tree if self._tree else \
                etree.HTML(self.page_source()) 
               
        self.orderbook.reset()

        # Parsing bid orderbook (assumes descending order)
        bid_prices = tree.xpath(self.bid_orderbook_price_xpath)
        bid_sizes = tree.xpath(self.bid_orderbook_size_xpath)
        max_bid_entries = min(self.max_orderbook_entries, len(bid_prices))

        for bid_price, bid_size in zip(bid_prices[:max_bid_entries], bid_sizes[:max_bid_entries]):
            self.orderbook.append_bid(
                self.convert_to_float(bid_price.text),
                self.convert_to_float(bid_size.text)
            )
        
        # Parsing bid orderbook (assumes ascending order)
        ask_prices = tree.xpath(self.ask_orderbook_price_xpath)
        ask_sizes = tree.xpath(self.ask_orderbook_size_xpath)
        max_ask_entries = min(self.max_orderbook_entries, len(ask_prices))

        for ask_price, ask_size in zip(ask_prices[:max_ask_entries], ask_sizes[:max_bid_entries]):     
            self.orderbook.append_ask(
                self.convert_to_float(ask_price.text),
                self.convert_to_float(ask_size.text)
            )

    def update_tradebook(self, tree = None) -> None:
        tree: etree._ElementTree = self._tree if self._tree else \
                etree.HTML(self.page_source())
        
        trade_timestamps = tree.xpath(self.trades_timestamp_xpath)
        trade_prices = tree.xpath(self.trades_price_xpath)
        trade_sizes = tree.xpath(self.trades_size_xpath)
        prev_timestamp = self.tradebook.get_timestamp()

        # Assumes most recent trade first
        for timestamp, price, size in zip(trade_timestamps, trade_prices, trade_sizes):
            timestamp = self.convert_to_timestamp(timestamp.text)

            if timestamp <= prev_timestamp:
                break
            
            self.tradebook.append_trade(timestamp, self.convert_to_float(price.text),
                    self.convert_to_float(size.text))

    # Destructors
    def close(self) -> None:
        RPAWebSurfer.close(self)
        MarketListenerBase.close(self)

if __name__ == "__main__":
    pass
