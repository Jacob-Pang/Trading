from . import ListenerBase

from pyutils.websurfer import XPathIdentifier
from pyutils.websurfer.rpa import RPAWebSurfer
from pyutils.websurfer.rpa.manager import RPAManager
from pyutils.websurfer.rpa.manager import rpa_manager

class RPAListenerBase (RPAWebSurfer, ListenerBase):
    def __init__(self, visual_automation: bool = False, chrome_browser: bool = True,
        headless_mode: bool = False, turbo_mode: bool = False, rpa_manager: RPAManager = rpa_manager,
        rpa_instance_id: int = None, chrome_scan_period: int = 0, sleeping_period: int = 0,
        engine_scan_period: int = 0, incognito_mode: bool = False):

        RPAWebSurfer.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                rpa_manager, rpa_instance_id, chrome_scan_period, sleeping_period,
                engine_scan_period, incognito_mode)

    # Abstract methods
    def get_url(self) -> str:
        raise NotImplementedError()

    def get_ready_element_xpath(self) -> XPathIdentifier:
        raise NotImplementedError()

    # Initializers
    def subscribe(self) -> None:
        self.restart()
        self.rpa.url(self.get_url())

    def ready(self) -> bool:
        return self.rpa.exist(self.get_ready_element_xpath().as_xpath())    
    
    # Destructors
    def close(self) -> None:
        ListenerBase.close(self)
        RPAWebSurfer.close(self)

if __name__ == "__main__":
    pass
