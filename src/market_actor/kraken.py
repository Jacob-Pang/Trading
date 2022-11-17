from . import MarketActorBase
from krakipy import KrakenAPI

# Transformations from currencies to tickers
_ticker_mapping = {
    "ETC":  "XETC",
    "ETH":  "XETH",
    "LTC":  "XLTC",
    "MLN":  "XMLN",
    "REP":  "XREP",
    "BTC":  "XXBT",
    "DOGE": "XXDG",
    "XLM":  "XXLM",
    "XRP":  "XXRP",
    "REP":  "XREP",
    "MLN":  "XMLN",
    "XMR":  "XXMR",
    "ZEC":  "XZEC",
    "EUR":  "ZEUR",
    "USD":  "ZUSD",
    "AUD":  "ZAUD",
    "GBP":  "ZGBP",
    "JPY":  "ZJPY",
}

_markets_to_tickers = None

def setup_markets_to_tickers() -> None:
    global _markets_to_tickers

    client = KrakenAPI()
    ticker_pdf = client.get_tradable_asset_pairs().reset_index()
    ticker_pdf["market"] = list(zip(ticker_pdf["base"], ticker_pdf["quote"]))
    ticker_pdf = ticker_pdf.set_index("market")

    _markets_to_tickers = ticker_pdf["index"].to_dict()

def get_ticker(market: tuple[str, str]) -> str:
    global _markets_to_tickers

    if not _markets_to_tickers:
        setup_markets_to_tickers()

    base, quote = market

    if base in _ticker_mapping:
        base = _ticker_mapping.get(base)

    if quote in _ticker_mapping:
        quote = _ticker_mapping.get(quote)

    if (base, quote) in _markets_to_tickers:
        return _markets_to_tickers.get((base, quote))

    return None


class KrakenActorBase (MarketActorBase):
    def __init__(self, api_key: str, api_key_secret: str) -> None:
        self.client = KrakenAPI(api_key, api_key_secret)

    def get_name(self) -> str:
        return "Kraken"

class KrakenTaker (KrakenActorBase):
    def get_transact_fee_rate(self, market: tuple[str, str]) -> float:
        return 0.26 / 100 # 0.26 %

    def place_buy_order(self, market: tuple[str, str], price: float, size: float) -> None:
        self.client.add_standard_order(get_ticker(market), "buy", "market", volume=size)

    def place_sell_order(self, market: tuple[str, str], price: float, size: float) -> None:
        self.client.add_standard_order(get_ticker(market), "sell", "market", volume=size)

if __name__ == "__main__":
    pass