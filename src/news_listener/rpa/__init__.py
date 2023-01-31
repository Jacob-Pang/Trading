import datetime

from .. import NewsListenerBase, News
from ...listener.rpa import RPAListenerBase
from pyutils.websurfer.rpa.manager import RPAManager
from pyutils.websurfer.rpa.manager import rpa_manager

class RPANewsListenerBase (RPAListenerBase, NewsListenerBase):
    def __init__(self, set_timestamp: datetime.datetime = None, max_capacity: int = 100,
        visual_automation: bool = False, chrome_browser: bool = True, headless_mode: bool = False,
        turbo_mode: bool = False, rpa_manager: RPAManager = rpa_manager, rpa_instance_id: int = None,
        chrome_scan_period: int = 0, sleeping_period: int = 0, engine_scan_period: int = 0,
        incognito_mode: bool = False) -> None:

        RPAListenerBase.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                rpa_manager, rpa_instance_id, chrome_scan_period, sleeping_period,
                engine_scan_period, incognito_mode)

        NewsListenerBase.__init__(self, set_timestamp, max_capacity)

    def get(self) -> News:
        return NewsListenerBase.get(self)

if __name__ == "__main__":
    pass
