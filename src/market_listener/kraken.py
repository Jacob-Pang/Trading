from . import MarketListenerBase
from pyutils.websurfer import XPathIdentifier
from pyutils.websurfer.rpa import RPAWebSurfer

# Update: Kraken cannot be run in headless_mode
class KrakenListener (MarketListenerBase, RPAWebSurfer):
    # Xpaths
    curr_price_xpath     = "//div[@id='price-ticker']/span[2]"
    curr_bid_price_xpath = "//div[@id='bids-list']/div/div/div[2]"
    curr_bid_size_xpath  = "//div[@id='bids-list']/div/div/div[3]"
    curr_ask_price_xpath = "//div[@id='asks-list']/div/div/div[2]"
    curr_ask_size_xpath  = "//div[@id='asks-list']/div/div/div[3]"
    bid_orderbook_xpath  = "//div[@id='bids-list']/div/div"
    ask_orderbook_xpath  = "//div[@id='asks-list']/div/div"

    def __init__(self, market: tuple[str, str], max_orderbook_entries: int = 10, visual_automation: bool = False,
        chrome_browser: bool = True, headless_mode: bool = False, turbo_mode: bool = False) -> None:

        MarketListenerBase.__init__(self, market, max_orderbook_entries)

        # Listening with minimum delays
        RPAWebSurfer.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                chrome_scan_period=0, looping_delay=False, sleep_period=0,
                engine_scan_period=0)

    # Parsers
    def parse_bid_orderbook(self, bid_orderbook: str) -> None:
        # Format caa 14 Nov 2022:
        # // descending
        # (num_entries - 1) x short_price
        # current_price
        # (num_entries - 1) x trailing_price
        # current_size
        # (num_entries - 1) x size
        bid_orderbook = bid_orderbook.split('\n')
        num_entries = (len(bid_orderbook) + 1) // 4
        self.max_orderbook_entries = min(self.max_orderbook_entries, num_entries)

        # Parse prices up to max_entries
        current_price = float(bid_orderbook[num_entries - 1])
        current_size = float(bid_orderbook[2 * num_entries - 1].replace(' ', ''))

        # Update current bid
        self.orderbook.append_bid(current_price, current_size)

        for entry in range(self.max_orderbook_entries - 1):
            short_price = bid_orderbook[entry]
            trailing_price = bid_orderbook[num_entries + entry]
            size = bid_orderbook[2 * num_entries + entry]

            self.orderbook.append_bid(
                float((short_price + trailing_price).replace(' ', '')),
                float(size.replace(' ', ''))
            )

    def parse_ask_orderbook(self, ask_orderbook: str) -> None:
        # Format caa 15 Nov 2022: // Note: format seems unstable
        # // descending
        # (num_entries - 2) x short_price
        # // space
        # highest_price
        # (num_entries - 2) x trailing_price
        # current_price
        # (num_entries - 1) x size
        # current_size
        ask_orderbook = ask_orderbook.split('\n')
        num_entries = (len(ask_orderbook) + 1) // 4
        self.max_orderbook_entries = min(self.max_orderbook_entries, num_entries - 1) # Dropping highest_price

        # Parse prices up to max_entries
        for entry in range(2, self.max_orderbook_entries + 2):
            short_price = ask_orderbook[num_entries - entry]
            trailing_price = ask_orderbook[2 * num_entries - entry]
            size = ask_orderbook[3 * num_entries - entry]

            self.orderbook.append_ask(
                float((short_price + trailing_price).replace(' ', '')),
                float(size.replace(' ', ''))
            )


    def subscribe(self) -> None:
        base, quote = self.market
        self.rpa.url(f"https://trade.kraken.com/charts/KRAKEN:{base}-{quote}")

    def rendered(self) -> bool:
        return self.rpa.exist(self.bid_orderbook_xpath)

    def get_name(self) -> str:
        return "Kraken"

    def get_current_price(self) -> float:
        return float(self.get_text(XPathIdentifier(self.curr_price_xpath)))

    def get_current_bid(self) -> tuple[float, float]:
        bid_price = float(self.get_text(XPathIdentifier(self.curr_bid_price_xpath)).split('\n')[0])
        bid_size = float(self.get_text(XPathIdentifier(self.curr_bid_size_xpath)).split('\n')[0]
                .replace(' ', ''))
        
        return bid_price, bid_size

    def get_current_ask(self) -> tuple[float, float]:
        ask_price = float(self.get_text(XPathIdentifier(self.curr_ask_price_xpath)).split('\n')[-1])
        ask_size = float(self.get_text(XPathIdentifier(self.curr_ask_size_xpath)).split('\n')[-1]
                .replace(' ', ''))
        
        return ask_price, ask_size
    
    def update_orderbook(self) -> None:
        # For some reason the HTML cannot be parsed: have to read the text directly from the webpage instead.
        # Reduce delay between snapshots by reading before parsing
        bid_orderbook = self.get_text(XPathIdentifier(self.bid_orderbook_xpath))
        ask_orderbook = self.get_text(XPathIdentifier(self.ask_orderbook_xpath))

        self.orderbook.reset()
        self.parse_bid_orderbook(bid_orderbook)
        self.parse_ask_orderbook(ask_orderbook)

    def close(self) -> None:
        return RPAWebSurfer.close(self)

if __name__ == "__main__":
    pass