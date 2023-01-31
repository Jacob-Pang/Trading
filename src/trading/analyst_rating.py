from collections.abc import Iterable
from pyutils.events import wait_for
from pyutils.websurfer import WebsurferBase, XPathIdentifier
from pyutils.websurfer.rpa import RPAWebSurfer

def get_nasdaq_analyst_rating(stock_tickers: (str | Iterable[str]), websurfer: WebsurferBase = None) \
    -> (float | list[float]):

    if not websurfer:
        with RPAWebSurfer() as websurfer:
            return get_nasdaq_analyst_rating(stock_tickers, websurfer)

    if isinstance(stock_tickers, str):
        return get_nasdaq_analyst_rating([stock_tickers], websurfer)[0]

    nasdaq_rating_map: dict[str, float] = {
        "Strong Buy": 1,
        "Buy": .5,
        "Hold": 0,
        "Underperform": -.5,
        "Sell": -1
    }

    rating_ident = XPathIdentifier("//span[@class='upgrade-downgrade-b__rating-value']")
    stock_ratings = []

    for stock_ticker in stock_tickers:
        websurfer.get(f"https://www.nasdaq.com/market-activity/stocks/{stock_ticker}/analyst-research")
        assert wait_for(websurfer.exists, timeout=10, element_identifier=rating_ident)

        rating = nasdaq_rating_map[websurfer.get_text(rating_ident)]
        stock_ratings.append(rating)

    return stock_ratings

if __name__ == "__main__":
    pass