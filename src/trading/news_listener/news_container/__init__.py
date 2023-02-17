import datetime
from ..news import News

class NewsContainerBase:
    def __init__(self, max_capacity: int, similarity_treshold: float = .8):
        self.max_capacity = max_capacity
        self.similarity_treshold = similarity_treshold

        self.news_links = list[str]()
        self.link_to_news = dict[str, News]()
        self.reading_ptr = 0

    # Getters
    def get(self) -> (News | None):
        if self.reading_ptr >= len(self.news_links):
            return None

        self.reading_ptr += 1
        return self.link_to_news.get(self.news_links[self.reading_ptr - 1])

    def get_similarity(self, news: News) -> float:
        # Returns a score from -1 to 1
        return 0

    def get_latest_timestamp(self) -> datetime.datetime:
        if self.news_links:
            latest_news = self.link_to_news.get(self.news_links[-1])
            return latest_news.timestamp

        return datetime.datetime(datetime.MINYEAR, 1, 1)

    # Mutator
    def append_news(self, news: News) -> bool:
        # Returns whether the news was appended as unseen (back of queue)
        if news.article_link in self.link_to_news:
            # Override existing news
            self.link_to_news[news.article_link] = news
            return False

        if news.timestamp < self.get_latest_timestamp():
            return False

        if self.get_similarity(news) > self.similarity_treshold:
            # Exceeds treshold for similarity in news
            return False

        self.news_links.append(news.article_link)
        self.link_to_news[news.article_link] = news

        if len(self.news_links) > self.max_capacity:
            oldest_news_link = self.news_links.pop(0)
            self.link_to_news.pop(oldest_news_link)
            self.reading_ptr = max(self.reading_ptr - 1, 0)
        
        return True

if __name__ == "__main__":
    pass