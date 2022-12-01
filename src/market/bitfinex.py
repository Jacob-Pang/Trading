from .spot import Spot
from .derivative import Derivative

# from https://api-pub.bitfinex.com/v2/conf/pub:list:pair:exchange
spot_markets = ["1INCH:USD","1INCH:UST","AAABBB","AAVE:USD","AAVE:UST","ADABTC","ADAUSD","ADAUST","AIXUSD","AIXUST","ALBT:USD","ALGBTC","ALGUSD","ALGUST","AMPBTC","AMPUSD","AMPUST","ANCUSD","ANCUST","ANTBTC","ANTETH","ANTUSD","APENFT:USD","APENFT:UST","APEUSD","APEUST","APTUSD","APTUST","ATLAS:USD","ATLAS:UST","ATOBTC","ATOETH","ATOUSD","ATOUST","AVAX:BTC","AVAX:USD","AVAX:UST","AXSUSD","AXSUST","B2MUSD","B2MUST","BALUSD","BALUST","BAND:USD","BAND:UST","BATUSD","BATUST","BCHABC:USD","BCHN:USD","BEST:USD","BFTUSD","BMIUSD","BMNBTC","BMNUSD","BNTUSD","BOBA:USD","BOBA:UST","BOOUSD","BOOUST","BOSON:USD","BOSON:UST","BSVBTC","BSVUSD","BTC:CNHT","BTC:MXNT","BTC:XAUT","BTCEUR","BTCEUT","BTCGBP","BTCJPY","BTCMIM","BTCTRY","BTCUSD","BTCUST","BTGBTC","BTGUSD","BTSE:USD","BTTUSD","CCDBTC","CCDUSD","CCDUST","CELUSD","CELUST","CHEX:USD","CHSB:BTC","CHSB:USD","CHSB:UST","CHZUSD","CHZUST","CLOUSD","CNH:CNHT","COMP:USD","COMP:UST","CONV:USD","CONV:UST","CRVUSD","CRVUST","DAIBTC","DAIETH","DAIUSD","DGBUSD","DOGE:BTC","DOGE:USD","DOGE:UST","DORA:USD","DORA:UST","DOTBTC","DOTUSD","DOTUST","DSHBTC","DSHUSD","DUSK:BTC","DUSK:USD","DVFUSD","EDOUSD","EGLD:USD","EGLD:UST","ENJUSD","EOSBTC","EOSETH","EOSEUR","EOSUSD","EOSUST","ETCBTC","ETCUSD","ETCUST","ETH2X:ETH","ETH2X:USD","ETH2X:UST","ETH:MXNT","ETH:XAUT","ETHBTC","ETHEUR","ETHEUT","ETHGBP","ETHJPY","ETHUSD","ETHUST","ETHW:USD","ETHW:UST","ETPUSD","EURUST","EUSUSD","EUT:MXNT","EUTEUR","EUTUSD","EUTUST","EXOUSD","FBTUSD","FBTUST","FCLUSD","FCLUST","FETUSD","FETUST","FILUSD","FILUST","FORTH:USD","FORTH:UST","FTMUSD","FTMUST","FTTUSD","FTTUST","FUNUSD","GALA:USD","GALA:UST","GBPEUT","GBPUST","GNOUSD","GNTUSD","GRTUSD","GRTUST","GTXUSD","GTXUST","GXTUSD","GXTUST","HECUSD","HECUST","HIXUSD","HIXUST","HMTUSD","HMTUST","ICEUSD","ICPBTC","ICPUSD","ICPUST","IDXUSD","IDXUST","IOTBTC","IOTETH","IOTUSD","IQXUSD","JASMY:USD","JASMY:UST","JPYUST","JSTBTC","JSTUSD","JSTUST","KAIUSD","KAIUST","KANUSD","KANUST","KNCBTC","KNCUSD","KSMUSD","KSMUST","LEOBTC","LEOETH","LEOUSD","LEOUST","LINK:USD","LINK:UST","LRCUSD","LTCBTC","LTCUSD","LTCUST","LUNA2:USD","LUNA2:UST","LUNA:USD","LUNA:UST","LUXO:USD","LYMUSD","MATIC:BTC","MATIC:USD","MATIC:UST","MIMUSD","MIMUST","MIRUSD","MIRUST","MKRUSD","MKRUST","MLNUSD","MNABTC","MNAUSD","MOBUSD","MOBUST","MXNT:USD","NEAR:USD","NEAR:UST","NEOBTC","NEOUSD","NEOUST","NEXO:BTC","NEXO:USD","NEXO:UST","OCEAN:USD","OCEAN:UST","OMGBTC","OMGETH","OMGUSD","OMNUSD","OXYUSD","OXYUST","PASUSD","PAXUSD","PAXUST","PLANETS:USD","PLANETS:UST","PLUUSD","PNGUSD","PNKUSD","POLC:USD","POLC:UST","POLIS:USD","POLIS:UST","QRDO:USD","QRDO:UST","QTFBTC","QTFUSD","QTMBTC","QTMUSD","RBTBTC","RBTUSD","REEF:USD","REEF:UST","REPUSD","REQUSD","RLYUSD","RLYUST","ROSE:USD","ROSE:UST","RRTUSD","SAND:USD","SAND:UST","SENATE:USD","SENATE:UST","SGBUSD","SGBUST","SHFT:USD","SHFT:UST","SHIB:USD","SHIB:UST","SIDUS:USD","SIDUS:UST","SMRUSD","SMRUST","SNTUSD","SNXUSD","SNXUST","SOLBTC","SOLUSD","SOLUST","SPELL:USD","SPELL:UST","SRMUSD","SRMUST","STGUSD","STGUST","STJUSD","SUKU:USD","SUKU:UST","SUNUSD","SUNUST","SUSHI:USD","SUSHI:UST","SWEAT:USD","SWEAT:UST","SXXUSD","SXXUST","TERRAUST:USD","TERRAUST:UST","TESTBTC:TESTUSD","TESTBTC:TESTUSDT","THETA:USD","THETA:UST","TLOS:USD","TLOS:UST","TRADE:USD","TRADE:UST","TREEB:USD","TREEB:UST","TRXBTC","TRXETH","TRXEUR","TRXUSD","TRXUST","TRYUST","TSDUSD","TSDUST","UDCUSD","UDCUST","UNIUSD","UNIUST","UOSBTC","UOSUSD","UST:CNHT","UST:MXNT","USTUSD","UTKUSD","VEEUSD","VELO:USD","VELO:UST","VETBTC","VETUSD","VETUST","VRAUSD","VRAUST","VSYUSD","WAVES:USD","WAVES:UST","WAXUSD","WBTUSD","WILD:USD","WILD:UST","WNCG:USD","WNCG:UST","WOOUSD","WOOUST","XAUT:BTC","XAUT:USD","XAUT:UST","XCAD:USD","XCNUSD","XCNUST","XDCUSD","XDCUST","XLMBTC","XLMUSD","XLMUST","XMRBTC","XMRUSD","XMRUST","XRAUSD","XRDBTC","XRDUSD","XRPBTC","XRPUSD","XRPUST","XTZBTC","XTZUSD","XTZUST","XVGUSD","YFIUSD","YFIUST","ZCNUSD","ZECBTC","ZECUSD","ZILBTC","ZILUSD","ZMTUSD","ZMTUST","ZRXBTC","ZRXETH","ZRXUSD"]

class BitfinexSpot (Spot):
    def get_ticker(self) -> str:
        if self.get_query() in spot_markets:
            return f"t{self.get_query()}"

        if f"{self.base}{self.quote}" in spot_markets:
            return f"t{self.base}{self.quote}"
        
        raise Exception(f"Bitfinex does not support {Spot.get_ticker(self)}")

    def get_query(self) -> str:
        return f"{self.base}:{self.quote}"

class BitfinexDerivative (Derivative):
    # Supports only XXX-PERPs
    def __init__(self, ticker: str, execution_currency: str) -> None:
        Derivative.__init__(self, ticker, execution_currency)
        
        self.base = ticker.replace("-PERP", '')

    def get_ticker(self) -> str:
        return f"t{self.base}F0:USTF0"
    
    def get_query(self) -> str:
        return f"{self.base}F0:USTF0"

if __name__ == "__main__":
    pass