import datetime
import pandas as pd

class EarningsList:
    def __init__(self, earnings_list: pd.DataFrame):
        """ @param earnings_list (pd.DataFrame): dataframe with columns (release_datetime,
            stcok_ticker, eps_forecast).
        """
        self.earnings_list = earnings_list.drop_duplicates()

    def get_earnings_before_market_open(self, earnings_calendar: "EarningsCalendarBase",
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

    def get_earnings_after_market_close(self,  earnings_calendar: "EarningsCalendarBase",
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

class EarningsCalendarBase:
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

    def get_market_open_time(self) -> datetime.time:
        raise NotImplementedError()

    def get_market_close_time(self) -> datetime.time:
        raise NotImplementedError()

    def get_market_open_datetime(self, day: datetime.date) -> datetime.datetime:
        market_open_time = self.get_market_open_time()

        return datetime.datetime(year=day.year, month=day.month, day=day.day,
                hour=market_open_time.hour, minute=market_open_time.minute,
                second=market_open_time.second)

    def get_market_close_datetime(self, day: datetime.date) -> datetime.datetime:
        market_open_time = self.get_market_open_time()
        market_close_time = self.get_market_close_time()

        if market_close_time < market_open_time:
            day += datetime.timedelta(days=1)

        return datetime.datetime(year=day.year, month=day.month, day=day.day,
                hour=market_close_time.hour, minute=market_close_time.minute,
                second=market_close_time.second)

    def get_earnings_calendar(self, from_day: datetime.date = datetime.date.today(),
        to_day: datetime.date = None, days: int = 0, **kwargs) -> EarningsList:
        raise NotImplementedError()

    def get_post_release_calendar_day(self, release_datetimes: (pd.Series | EarningsList)) \
        -> list[datetime.date]:
        """ Gets the first calendar day during which the market has knowledge of the earnings.

        @param release_datetimes (pd.Series | EarningsList): the release datetimes or an
                EarningsList object.
        
        @returns post_release_calendar_day (list[datetime.date]): the first calendar
                day for which the market is open post-release of the earnings (
                    released before_market_open: same calendar day
                    released during_market_hours: same calendar day
                    released after_market_close: following calendar day
                ).
        """
        if isinstance(release_datetimes, EarningsList):
            return self.get_post_release_calendar_day(release_datetimes.earnings_list
                    ["release_datetime"])

        dates = release_datetimes.dt.date
        times = release_datetimes.dt.time

        market_open_time = self.get_market_open_time()
        market_close_time = self.get_market_close_time()

        return [
            date + datetime.timedelta(days=int(after_market_close))
            for date, after_market_close in zip(dates, times >= market_close_time)
        ] if market_close_time > market_open_time else [
            date - datetime.timedelta(days=int(before_market_close))
            for date, before_market_close in zip(dates, times < market_close_time)
        ]

if __name__ == "__main__":
    pass