
class TradingLogicInterface:
    def update(self) -> None:
        # Performs any updates to the TradingLogic
        pass

    def get_open_trade(self) -> tuple[float, float]:
        # Returns the current price and size to open a position at.
        raise NotImplementedError()

if __name__ == "__main__":
    pass