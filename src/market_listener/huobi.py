from . import MarketListenerBase
from lxml import etree
from pyutils.websurfer import XPathIdentifier
from pyutils.websurfer.rpa import RPAWebSurfer

class HuobiListener (MarketListenerBase, RPAWebSurfer):
    curr_price_xpath = "//div[@class='now-price']/dl/dt"

    # In descending order
    bid_orderbook_price_xpath = "//div[@class='list bids']/p/span[1]"
    bid_orderbook_size_xpath  = "//div[@class='list bids']/p/span[2]"
    bid_orderbook_accum_xpath = "//div[@class='list bids']/p/span[3]"

    # In ascending order
    ask_orderbook_price_xpath = "//div[@class='list asks']/p/span[1]"
    ask_orderbook_size_xpath  = "//div[@class='list asks']/p/span[2]"
    ask_orderbook_accum_xpath = "//div[@class='list asks']/p/span[3]"

    def __init__(self, market: tuple[str, str], max_orderbook_entries: int = 10, visual_automation: bool = False,
        chrome_browser: bool = True, headless_mode: bool = False, turbo_mode: bool = False) -> None:

        MarketListenerBase.__init__(self, market, max_orderbook_entries)

        # Listening with minimum delays
        RPAWebSurfer.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                chrome_scan_period=0, looping_delay=False, sleep_period=0,
                engine_scan_period=0)

    def subscribe(self) -> None:
        base, quote = self.market
        self.rpa.url(f"https://www.huobi.com/en-us/exchange/{base.lower()}_{quote.lower()}/")

    def rendered(self) -> bool:
        # The orderbook takes the longest to render
        return self.rpa.exist(self.ask_orderbook_price_xpath)

    def get_name(self) -> str:
        return "Huobi"

    def get_current_price(self) -> float:
        return float(self.get_text(XPathIdentifier(self.curr_price_xpath)))

    def get_current_bid(self) -> tuple[float, float]:
        bid_price = float(self.get_text(XPathIdentifier(self.bid_orderbook_price_xpath)))
        bid_size  = float(self.get_text(XPathIdentifier(self.bid_orderbook_size_xpath)))
        
        return bid_price, bid_size

    def get_current_ask(self) -> tuple[float, float]:
        ask_price = float(self.get_text(XPathIdentifier(self.ask_orderbook_price_xpath)))
        ask_size  = float(self.get_text(XPathIdentifier(self.ask_orderbook_size_xpath)))
        
        return ask_price, ask_size
    
    def update_orderbook(self) -> None:
        tree = etree.HTML(self.page_source())
        self.orderbook.reset()

        # Parsing bid orderbook
        bid_prices = tree.xpath(self.bid_orderbook_price_xpath)
        bid_sizes = tree.xpath(self.bid_orderbook_size_xpath)
        accum_bid_sizes = tree.xpath(self.bid_orderbook_accum_xpath)

        max_bid_entries = min(self.max_orderbook_entries, len(bid_prices))

        for bid_price, bid_size, accum_bid_size in zip(bid_prices[:max_bid_entries],
                bid_sizes[:max_bid_entries], accum_bid_sizes[:max_bid_entries]):
            
            self.orderbook.append_bid(
                float(bid_price.text),
                float(bid_size.text),
                float(accum_bid_size.text)
            )
        
        # Parsing bid orderbook
        ask_prices = tree.xpath(self.ask_orderbook_price_xpath)
        ask_sizes = tree.xpath(self.ask_orderbook_size_xpath)
        accum_ask_sizes = tree.xpath(self.ask_orderbook_accum_xpath)

        max_ask_entries = min(self.max_orderbook_entries, len(ask_prices))

        for ask_price, ask_size, accum_ask_size in zip(ask_prices[:max_ask_entries],
                ask_sizes[:max_bid_entries], accum_ask_sizes[:max_ask_entries]):
            
            self.orderbook.append_ask(
                float(ask_price.text),
                float(ask_size.text),
                float(accum_ask_size.text)
            )

    def close(self) -> None:
        return RPAWebSurfer.close(self)

if __name__ == "__main__":
    pass