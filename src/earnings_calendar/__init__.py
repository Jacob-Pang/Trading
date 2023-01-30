import datetime
import pandas as pd

class EarningsList:
    def __init__(self, earnings_list: pd.DataFrame):
        """ @param earnings_list (pd.DataFrame): dataframe with columns (release_time,
            stcok_ticker, eps_forecast).
        """
        self.earnings_list = earnings_list.drop_duplicates()

    def get_earnings_before_market_open(self, earnings_calendar: "EarningsCalendarInterface",
        calendar_day: datetime.date = datetime.date.today()) -> pd.DataFrame:
        """ Returns the earning releases before market open ( captures earnings released
            before market open and after market close on the previous business day ).
        
        @param earnings_calendar (EarningsCalendarInterface): the exchange earnings calendar
                that determines the market opening and closing times
        @param calendar_day (datetime.date, opt): the calendar day to use.
        
        @returns earnings_list (pd.DataFrame): the satisfying subset of the earnings_list.
        """
        market_open_datetime = earnings_calendar.get_market_open_datetime(calendar_day)
        prev_calendar_day = earnings_calendar.get_prev_calendar_day(calendar_day)
        prev_market_close_datetime = earnings_calendar.get_market_close_datetime(prev_calendar_day)
        
        return self.earnings_list[
            (self.earnings_list["release_datetime"] >= prev_market_close_datetime) &
            (self.earnings_list["release_datetime"] <= market_open_datetime)
        ]

    def get_earnings_after_market_close(self,  earnings_calendar: "EarningsCalendarInterface",
        calendar_day: datetime.date = datetime.date.today()) -> pd.DataFrame:
        """ Returns the earning releases after market open ( captures earnings released
            after market close and before market open on the following business day ).
        
        @param earnings_calendar (EarningsCalendarInterface): the exchange earnings calendar
                that determines the market opening and closing times
        @param calendar_day (datetime.date, opt): the calendar day to use.
        
        @returns earnings_list (pd.DataFrame): the satisfying subset of the earnings_list.
        """
        market_close_datetime = earnings_calendar.get_market_close_datetime(calendar_day)
        next_calendar_day = earnings_calendar.get_next_calendar_day(calendar_day)
        next_market_open_datetime = earnings_calendar.get_market_open_datetime(next_calendar_day)
        
        return self.earnings_list[
            (self.earnings_list["release_datetime"] >= market_close_datetime) &
            (self.earnings_list["release_datetime"] <= next_market_open_datetime)
        ]

    def __add__(self, other: "EarningsList") -> "EarningsList":
        return EarningsList(pd.concat([self.earnings_list, other.earnings_list]))

class EarningsCalendarInterface:
    @staticmethod
    def get_next_calendar_day(calendar_day: datetime.date) -> datetime.date:
        next_calendar_day: datetime.date = calendar_day + datetime.timedelta(days=1)

        while next_calendar_day.weekday() > 4:
            next_calendar_day += datetime.timedelta(days=1)

        return next_calendar_day

    @staticmethod
    def get_prev_calendar_day(calendar_day: datetime.date) -> datetime.date:
        next_calendar_day: datetime.date = calendar_day - datetime.timedelta(days=1)

        while next_calendar_day.weekday() > 4:
            next_calendar_day -= datetime.timedelta(days=1)

        return next_calendar_day

    def get_market_open_datetime(self, day: datetime.date) -> datetime.datetime:
        raise NotImplementedError()

    def get_market_close_datetime(self, day: datetime.date) -> datetime.datetime:
        raise NotImplementedError()

    def get_earnings_calendar(self, from_day: datetime.date = datetime.date.today(),
        to_day: datetime.date = None, days: int = 0, **kwargs) -> EarningsList:
        raise NotImplementedError()

if __name__ == "__main__":
    pass