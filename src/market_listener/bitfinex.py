from .rpa import RPAMarketListenerBase
from pyutils.websurfer import XPathIdentifier

class BitfinexListener (RPAMarketListenerBase):
    # xpaths
    curr_price_xpath = "//body/div[2]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/section[1]/div[1]/div[2]/div[2]/h5/span"
    bid_orderbook_size_xpath  = "//div[@class='book-bids bookViz-green book__side tour-book-bids']/div[3]/div/div/div[4]/span"
    bid_orderbook_price_xpath = "//div[@class='book-bids bookViz-green book__side tour-book-bids']/div[3]/div/div/div[6]/span"
    ask_orderbook_size_xpath  = "//div[@class='book-asks bookViz-red book__side tour-book-asks']/div[3]/div/div/div[4]/span"
    ask_orderbook_price_xpath = "//div[@class='book-asks bookViz-red book__side tour-book-asks']/div[3]/div/div/div[6]/span"

    def get_name(self) -> str:
        return "Bitfinex"

    def get_url(self) -> str:
        return f"https://trading.bitfinex.com/t/{self.market.get_query()}?type=exchange"

    def get_ready_element_xpath(self) -> XPathIdentifier:
        return XPathIdentifier(self.bid_orderbook_size_xpath)

    def convert_to_float(self, num_text: str) -> float:
        # number format 0,000.00 without spaces
        return float(num_text.replace(',', ''))
        
if __name__ == "__main__":
    pass