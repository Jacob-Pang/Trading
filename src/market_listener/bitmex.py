from . import MarketListenerBase
from lxml import etree
from pyutils.websurfer import XPathIdentifier
from pyutils.websurfer.rpa import RPAWebSurfer

class BitmexListener (MarketListenerBase, RPAWebSurfer):
    # Xpaths
    curr_price_xpath     = "//body/div[1]/main/div[2]/div[1]/div[1]/div/div[3]/div[1]/div[1]/span/span"
    curr_bid_price_xpath = "//body/div[1]/main/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[3]/div[3]/div[1]/div[2]"
    curr_bid_size_xpath  = "//body/div[1]/main/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[3]/div[3]/div[1]/div[3]"
    curr_ask_price_xpath = "//body/div[1]/main/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[3]/div[1]/div/div[20]/div[2]"
    curr_ask_size_xpath  = "//body/div[1]/main/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[3]/div[1]/div/div[20]/div[3]"
    bid_orderbook_xpath  = "//body/div[1]/main/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[3]/div[3]/div/div"
    ask_orderbook_xpath  = "//body/div[1]/main/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[3]/div[1]/div/div/div"

    def __init__(self, market: tuple[str, str], max_orderbook_entries: int = 10, visual_automation: bool = False,
        chrome_browser: bool = True, headless_mode: bool = False, turbo_mode: bool = False) -> None:

        MarketListenerBase.__init__(self, market, max_orderbook_entries)

        # Listening with minimum delays
        RPAWebSurfer.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                chrome_scan_period=0, looping_delay=False, sleep_period=0,
                engine_scan_period=0)

    def subscribe(self) -> None:
        quote, base = self.market

        if quote == "BTC":
            quote = "XBT"

        self.rpa.url(f"https://www.bitmex.com/spot/{quote}_{base}")

    def rendered(self) -> bool:
        # The orderbook takes the longest to render
        return self.rpa.exist(self.ask_orderbook_xpath)

    def get_name(self) -> str:
        return "BitMEX"

    def get_current_price(self) -> float:
        return float(self.get_text(XPathIdentifier(self.curr_price_xpath)).replace(',', ''))

    def get_current_bid(self) -> tuple[float, float]:
        bid_price = float(self.get_text(XPathIdentifier(self.curr_bid_price_xpath)).replace(',', ''))
        bid_size = float(self.get_text(XPathIdentifier(self.curr_bid_size_xpath)).replace(',', ''))
        
        return bid_price, bid_size

    def get_current_ask(self) -> tuple[float, float]:
        ask_price = float(self.get_text(XPathIdentifier(self.curr_ask_price_xpath)).replace(',', ''))
        ask_size = float(self.get_text(XPathIdentifier(self.curr_ask_size_xpath)).replace(',', ''))
        
        return ask_price, ask_size
    
    def update_orderbook(self) -> None:
        tree = etree.HTML(self.page_source())
        self.orderbook.reset()

        # Parsing bid orderbook
        bid_orderbook = tree.xpath(self.bid_orderbook_xpath)
        max_bid_entries = min(self.max_orderbook_entries, len(bid_orderbook) // 4)
        
        for entry in range(max_bid_entries):
            bid_price = bid_orderbook[4 * entry + 1].text
            bid_size = bid_orderbook[4 * entry + 2].text
            accum_bid_size = bid_orderbook[4 * entry + 3].text
            
            self.orderbook.append_bid(
                float(bid_price.replace(',', '')),
                float(bid_size),
                float(accum_bid_size)
            )

        # Parsing ask orderbook
        ask_orderbook = tree.xpath(self.ask_orderbook_xpath)[::-1] # Reverse to maintain ascending order
        max_ask_entries = min(self.max_orderbook_entries, len(ask_orderbook) // 4)
        
        for entry in range(max_ask_entries):
            accum_ask_size = ask_orderbook[4 * entry].text
            ask_size = ask_orderbook[4 * entry + 1].text
            ask_price = ask_orderbook[4 * entry + 2].text
            
            self.orderbook.append_ask(
                float(ask_price.replace(',', '')),
                float(ask_size),
                float(accum_ask_size)
            )

    def close(self) -> None:
        return RPAWebSurfer.close(self)

if __name__ == "__main__":
    pass