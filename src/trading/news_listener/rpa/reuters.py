import datetime
import requests

from lxml import etree
from . import RPANewsListenerBase
from ..news import News
from ..news_container import NewsContainerBase

from pyutils.events import wait_for
from pyutils.websurfer import XPathIdentifier
from pyutils.websurfer.rpa.manager import RPAManager
from pyutils.websurfer.rpa.manager import rpa_manager

class ReutersNewsListener (RPANewsListenerBase):
    def __init__(self, login_email: str, login_password: str, visual_automation: bool = False,
        chrome_browser: bool = True, headless_mode: bool = False, turbo_mode: bool = False,
        rpa_manager: RPAManager = rpa_manager, rpa_instance_id: int = None, chrome_scan_period: int = 0,
        sleeping_period: int = 0, engine_scan_period: int = 0, incognito_mode: bool = False,
        news_container: NewsContainerBase = None) -> None:

        RPANewsListenerBase.__init__(self, visual_automation, chrome_browser, headless_mode, turbo_mode,
                rpa_manager, rpa_instance_id, chrome_scan_period, sleeping_period, engine_scan_period,
                incognito_mode, news_container)

        self.login_email = login_email
        self.login_password = login_password

    def get_url(self) -> str:
        return "https://www.reuters.com/account/sign-in/"

    def get_ready_element_xpath(self) -> XPathIdentifier:
        return XPathIdentifier("//main/section/ul/li/div/div/a")

    def go_to_news_list(self) -> None:
        self.rpa.url("https://www.reuters.com/myview/all")

    def subscribe(self) -> None:
        RPANewsListenerBase.subscribe(self)

        email_input_ident = XPathIdentifier("//input[@name='email']")
        password_input_ident = XPathIdentifier("//input[@name='password']")

        self.input_text(email_input_ident, self.login_email)
        self.input_text(password_input_ident, self.login_password)

        submit_button_ident = XPathIdentifier("//button[@type='submit']")
        self.click_element(submit_button_ident)

        assert wait_for(self.exists, timeout=10, element_identifier=XPathIdentifier
                ("//a[@href='/world/']"))

        self.go_to_news_list()

    def update(self) -> None:
        with self._update_semaphore:
            self.go_to_news_list() # Refresh
            assert wait_for(self.ready, timeout=10)

            news_list_item_ident = XPathIdentifier("//main/section/ul/li/div/div/a")
            news_headline_ident = news_list_item_ident.get_child("/h5")
            news_description_ident = news_list_item_ident.get_child("/p")
            
            news_list_tree: etree._ElementTree = etree.HTML(self.page_source())
            news_stack = list[News]()

            for news_list_item_elem, news_headline_elem, news_description_elem in zip(
                    news_list_tree.xpath(news_list_item_ident.as_xpath()),
                    news_list_tree.xpath(news_headline_ident.as_xpath()),
                    news_list_tree.xpath(news_description_ident.as_xpath())
                ):

                headline = news_headline_elem.text
                description = news_description_elem.text
                article_link = "https://www.reuters.com" + news_list_item_elem.attrib["href"]

                if article_link in self._news_container.link_to_news:
                    continue

                # Currently Reuters support requests
                article_tree = etree.HTML(requests.get(article_link).text)

                date: str = article_tree.xpath("//header/div/div/time/span[2]")[0].text
                time: str = article_tree.xpath("//header/div/div/time/span[3]")[0].text
                time = ' '.join(time.split(' ')[:2])

                timestamp = datetime.datetime.strptime(f"{date} {time}", "%B %d, %Y %I:%M %p") \
                        + datetime.timedelta(hours=8)

                if timestamp < self._news_container.get_latest_timestamp():
                    break

                news_stack.append(News(headline, article_link, description, timestamp))

            for news in news_stack:
                self.append_news(news)

if __name__ == "__main__":
    pass