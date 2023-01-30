import datetime
import pandas as pd

from pyutils.events import wait_for
from pyutils.websurfer import WebsurferBase, XPathIdentifier
from pyutils.websurfer.rpa import RPAWebSurfer

from . import EarningsCalendarInterface, EarningsList

class NasdaqEarningsCalendar (EarningsCalendarInterface):
    def get_market_open_datetime(self, day: datetime.date) -> datetime.datetime:
        return datetime.datetime(year=day.year, month=day.month, day=day.day, hour=14, minute=30)

    def get_market_close_datetime(self, day: datetime.date) -> datetime.datetime:
        return datetime.datetime(year=day.year, month=day.month, day=day.day, hour=21)

    def get_earnings_calendar(self, from_day: datetime.date = datetime.date.today(),
        to_day: datetime.date = None, days: int = 0, websurfer: WebsurferBase = None) \
        -> EarningsList:
        """
        """
        if not websurfer:
            with RPAWebSurfer() as websurfer:
                return self.get_earnings_calendar(from_day=from_day, to_day=to_day,
                        days=days, websurfer=websurfer)

        if not to_day:
            to_day = from_day + datetime.timedelta(days=days)

        websurfer.get("https://www.nasdaq.com/market-activity/earnings")

        # Element identifiers using xpath
        curr_calendar_day_ident = XPathIdentifier("//button[@class='time-belt__item time-belt__item--active']")
        advance_prev_day_belt_ident = XPathIdentifier("//button[@class='time-belt__prev']")
        advance_next_day_belt_ident = XPathIdentifier("//button[@class='time-belt__next']")

        table_row_ident = XPathIdentifier("//tbody[@class='market-calendar-table__body']" +
                "/tr[@class='market-calendar-table__row']")

        release_time_ident = table_row_ident.get_child("th[@data-column='time']/div/img")
        stock_ticker_ident = table_row_ident.get_child("td[@data-column='symbol']/div/a")
        eps_forecast_ident = table_row_ident.get_child("td[@data-column='epsForecast']/div")

        table_pages_ident = XPathIdentifier("div[@class='pagination__pages']")
        curr_table_page_ident = table_pages_ident.get_child("button[@class='pagination__page pagination__page--active']")
        advance_next_page_ident = XPathIdentifier("//button[@class='pagination__next']")

        earnings_list = list[tuple[datetime.datetime, str, float]]()

        def get_curr_calendar_day() -> datetime.date:
            curr_calendar_day_elem = websurfer.find_elements(curr_calendar_day_ident)[0]

            return datetime.date(
                year=int(curr_calendar_day_elem.attrib["data-year"]),
                month=int(curr_calendar_day_elem.attrib["data-month"]),
                day=int(curr_calendar_day_elem.attrib["data-day"])
            )

        def get_calendar_day_ident(calendar_day: datetime.date) -> XPathIdentifier:
            return XPathIdentifier("//button[" + " and ".join([
                    "@class='time-belt__item'",
                    f"@data-year='{calendar_day.year}'",
                    f"@data-month='{calendar_day.month:02}'",
                    f"@data-day='{calendar_day.day:02}'"
                ]) + "]")

        def advance_calendar_day(curr_calendar_day: datetime.date, advance_to_day_ident: XPathIdentifier,
            advance_belt_ident: XPathIdentifier) -> None:

            def calendar_day_advanced_pred(curr_calendar_day: datetime.date,
                advance_to_day_ident: XPathIdentifier) -> bool:

                if get_curr_calendar_day() != curr_calendar_day:
                    return True

                # Reclick element again
                websurfer.click_element(advance_to_day_ident)
                return False

            while not websurfer.exists(advance_to_day_ident):
                websurfer.click_element(advance_belt_ident)

            websurfer.click_element(advance_to_day_ident)
            assert wait_for(calendar_day_advanced_pred, timeout=10, curr_calendar_day=curr_calendar_day,
                    advance_to_day_ident=advance_to_day_ident)

        def parse_table(curr_calendar_day: datetime.date):
            def advanced_table_page_pred(websurfer: WebsurferBase, curr_table_page: int,
                curr_table_page_ident: XPathIdentifier) -> bool:
                return curr_table_page < int(websurfer.find_elements(curr_table_page_ident).text)

            pages = len(websurfer.find_elements(table_pages_ident.get_child("/button"))) \
                    if websurfer.exists(table_pages_ident) else 1

            for page_num in range(1, pages + 1): # Iterate over table pages
                for release_time_elem, stock_ticker_elem, eps_forecast_elem in zip(
                    websurfer.find_elements(release_time_ident),
                    websurfer.find_elements(stock_ticker_ident),
                    websurfer.find_elements(eps_forecast_ident)
                    ):

                    release_datetime = self.get_market_open_datetime(curr_calendar_day) \
                            if release_time_elem.attrib["alt"] == "time-pre-market" else \
                            self.get_market_close_datetime(curr_calendar_day)

                    eps_forecast: str = eps_forecast_elem.text

                    if eps_forecast:
                        eps_forecast = -float(eps_forecast.removeprefix('($').removesuffix(')')) \
                                if eps_forecast.startswith('(') else \
                                float(eps_forecast.removeprefix('$'))
                    
                    earnings_list.append((release_datetime, stock_ticker_elem.text, eps_forecast))

                if page_num < pages:
                    websurfer.click_element(advance_next_page_ident)
                    assert wait_for(advanced_table_page_pred, timeout=10, websurfer=websurfer,
                            curr_table_page=page_num, curr_table_page_ident=curr_table_page_ident)

        assert wait_for(websurfer.exists, timeout=10, element_identifier=curr_calendar_day_ident)
        curr_calendar_day = get_curr_calendar_day()

        if curr_calendar_day > from_day:
            # Iterate over the calendar days backwards
            while curr_calendar_day > from_day:
                advance_calendar_day(
                    curr_calendar_day,
                    get_calendar_day_ident(self.get_prev_calendar_day(curr_calendar_day)),
                    advance_prev_day_belt_ident
                )

                curr_calendar_day = get_curr_calendar_day()
                parse_table(curr_calendar_day)

            websurfer.get("https://www.nasdaq.com/market-activity/earnings")

        # Iterate over the calendar days forward
        while curr_calendar_day <= to_day:
            if curr_calendar_day >= from_day:
                parse_table(curr_calendar_day)

            advance_calendar_day(
                curr_calendar_day,
                get_calendar_day_ident(self.get_next_calendar_day(curr_calendar_day)),
                advance_next_day_belt_ident
            )

            curr_calendar_day = get_curr_calendar_day()

        earnings_list = pd.DataFrame(earnings_list, columns=["release_datetime",
                "stock_ticker", "eps_forecast"])

        return EarningsList(earnings_list)

if __name__ == "__main__":
    pass