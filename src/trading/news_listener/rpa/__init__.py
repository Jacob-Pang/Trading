from .. import NewsListenerBase
from ..news import News
from ..news_container import NewsContainerBase
from ...listener.rpa import RPAListenerBase
from pyutils.websurfer.rpa.manager import RPAManager
from pyutils.websurfer.rpa.manager import rpa_manager

class RPANewsListenerBase (RPAListenerBase, NewsListenerBase):
    def __init__(self, visual_automation: bool = False, chrome_browser: bool = True,
        headless_mode: bool = False, turbo_mode: bool = False, rpa_manager: RPAManager = rpa_manager,
        rpa_instance_id: int = None, chrome_scan_period: int = 0, sleeping_period: int = 0,
        engine_scan_period: int = 0, incognito_mode: bool = False, news_container: NewsContainerBase = None) \
        -> None:

        RPAListenerBase.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                rpa_manager, rpa_instance_id, chrome_scan_period, sleeping_period,
                engine_scan_period, incognito_mode)

        NewsListenerBase.__init__(self, news_container)

    def get(self) -> News:
        return NewsListenerBase.get(self)

if __name__ == "__main__":
    pass
