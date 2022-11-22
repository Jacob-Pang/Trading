from .rpa import RPAMarketListenerBase
from pyutils.websurfer import XPathIdentifier

class HuobiListener (RPAMarketListenerBase):
    # xpaths
    curr_price_xpath = "//div[@class='now-price']/dl/dt"
    bid_orderbook_price_xpath = "//div[@class='list bids']/p/span[1]"
    bid_orderbook_size_xpath  = "//div[@class='list bids']/p/span[2]"
    ask_orderbook_price_xpath = "//div[@class='list asks']/p/span[1]"
    ask_orderbook_size_xpath  = "//div[@class='list asks']/p/span[2]"

    def get_name(self) -> str:
        return "Huobi"

    def get_url(self) -> str:
        base, quote = self.market
        return f"https://www.huobi.com/en-us/exchange/{base.lower()}_{quote.lower()}/"

    def get_ready_element_xpath(self) -> XPathIdentifier:
        return XPathIdentifier(self.ask_orderbook_price_xpath)

    def convert_to_float(self, num_text: str) -> float:
        # perfect number format
        return float(num_text)

if __name__ == "__main__":
    pass