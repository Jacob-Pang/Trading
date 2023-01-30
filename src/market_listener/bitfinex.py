import time

from lxml import etree
from .rpa import RPAMarketListenerBase
from pyutils.websurfer import XPathIdentifier
from pyutils.websurfer.rpa.manager import RPAManager

class BitfinexListener (RPAMarketListenerBase):
    # xpaths
    curr_price_xpath = "//body/div[2]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/section[1]/div[1]/div[2]/div[2]/h5/span"
    bid_orderbook_size_xpath  = "//div[@class='book-bids bookViz-green book__side tour-book-bids']/div[3]/div/div/div[4]/span"
    bid_orderbook_price_xpath = "//div[@class='book-bids bookViz-green book__side tour-book-bids']/div[3]/div/div/div[6]/span"
    ask_orderbook_size_xpath  = "//div[@class='book-asks bookViz-red book__side tour-book-asks']/div[3]/div/div/div[4]/span"
    ask_orderbook_price_xpath = "//div[@class='book-asks bookViz-red book__side tour-book-asks']/div[3]/div/div/div[6]/span"
    trades_timestamp_xpath = "//div[@class='trades-table']/div[2]/div/div[2]/div/span"
    trades_price_xpath = "//div[@class='trades-table']/div[2]/div/div[3]/div/span/span[1]"
    trades_size_xpath  = "//div[@class='trades-table']/div[2]/div/div[4]/div/span/span[1]"

    current_day_timestamp = 0

    def __init__(self, market_query: str, tradebook_capacity: int = 100, visual_automation: bool = False,
        chrome_browser: bool = True, headless_mode: bool = False, turbo_mode: bool = False,
        rpa_manager: RPAManager = ..., rpa_instance_id: int = None, chrome_scan_period: int = 0,
        sleeping_period: int = 0, engine_scan_period: int = 0, incognito_mode: bool = False) -> None:

        RPAMarketListenerBase.__init__(self, tradebook_capacity, visual_automation, chrome_browser,
                headless_mode, turbo_mode, rpa_manager, rpa_instance_id, chrome_scan_period,
                sleeping_period,engine_scan_period, incognito_mode)

        self.market_query = market_query

    def get_name(self) -> str:
        return f"bitfinex_listener_on_{self.market_query}"

    def get_url(self) -> str:
        return f"https://trading.bitfinex.com/t/{self.market_query}?type=exchange"

    def get_ready_element_xpath(self) -> XPathIdentifier:
        return XPathIdentifier(self.bid_orderbook_size_xpath)

    def convert_to_float(self, num_text: str) -> float:
        # number format 0,000.00 without spaces
        return float(num_text.replace(',', ''))
    
    def convert_to_timestamp(self, timestamp_text: str) -> int:
        # timestamp format HH:MM:SS
        current_time = int(time.time())

        if self.current_day_timestamp < (current_time - 86400):
            self.current_day_timestamp = current_time - (current_time % 86400) # 60s * 60m * 24h

        h, m, s = timestamp_text.split(':')
        timestamp = self.current_day_timestamp + (int(h) * 3600) + (int(m) * 60) + int(s)

        if timestamp > current_time:
            timestamp -= 86400

        return timestamp

    def update_tradebook(self, tree = None) -> None:
        # Override method due to unorthodox HTML
        if tree is None:
            tree = etree.HTML(self.page_source())
        
        trade_timestamps = tree.xpath(self.trades_timestamp_xpath)
        trade_prices = tree.xpath(self.trades_price_xpath)
        trade_sizes = tree.xpath(self.trades_size_xpath)
        prev_timestamp = self.tradebook.get_timestamp()

        for timestamp, price, size in zip(trade_timestamps, trade_prices, trade_sizes):
            timestamp = self.convert_to_timestamp(timestamp.text)

            if timestamp <= prev_timestamp:
                break
            
            # Edit *********************************************************************
            price_text = price.text if price.text else ''.join(element.text for element
                    in price.getchildren())

            size_text = size.text if size.text else ''.join(element.text for element
                    in size.getchildren())

            self.tradebook.append_trade(timestamp, self.convert_to_float(price_text),
                    self.convert_to_float(size_text))
            # **************************************************************************

if __name__ == "__main__":
    pass