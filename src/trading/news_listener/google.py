from GoogleNews import GoogleNews

from . import NewsListenerBase
from .news import News
from .news_container import NewsContainerBase

class GoogleNewsListener (NewsListenerBase):
    def __init__(self, query: str, news_container: NewsContainerBase = None) -> None:
        NewsListenerBase.__init__(self, news_container)
        self.query = query
        self._google_news = GoogleNews(period="1h")
    
    def update(self) -> None:
        with self._update_semaphore:
            self._google_news.search(self.query)
            news_list: list[News] = [
                News(result["title"], result["link"], result['desc'], result["datetime"])
                for result in self._google_news.results()
            ]

            for news in sorted(news_list, key=lambda n: n.timestamp):
                self._news_container.append_news(news)

if __name__ == "__main__":
    pass