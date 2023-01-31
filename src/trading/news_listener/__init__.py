import datetime
from ..listener import ListenerBase

class News:
    def __init__(self, timestamp: datetime.datetime, headline: str, article_link: str,
        description: str) -> None:

        self.timestamp = timestamp
        self.headline = headline
        self.article_link = article_link
        self.description = description

    def as_telegram_message(self) -> str:
        return f"<b>{self.headline}</b>\r{self.timestamp.strftime(r'%b %d, %Y %I:%M %p')} GMT\r" \
                + f"{self.article_link}\r\r{self.description}"

class NewsListenerBase (ListenerBase):
    def __init__(self, set_timestamp: datetime.datetime = None, max_capacity: int = 100) -> None:
        self.max_capacity = max_capacity
        self.init_timestamp = set_timestamp if set_timestamp else datetime.datetime.now()
        self.news_list = list[News]()
        self.read_pointer = 0

    # Getters
    def get(self) -> (News | None):
        # Returns one unread news and consumes the read_pointer in the process
        if self.read_pointer == len(self.news_list):
            return None

        news = self.news_list[self.read_pointer]
        self.read_pointer += 1

        return news

    def get_last_timestamp(self) -> float:
        if self.news_list:
            return self.news_list[-1].timestamp

        return self.init_timestamp

    def get_news(self, from_timestamp: datetime.datetime = None) -> list[News]:
        if not from_timestamp:
            return self.news_list[self.read_pointer:]

        for read_pointer in range(len(self.news_list)):
            if self.news_list[read_pointer].timestamp > from_timestamp:
                return self.news_list[read_pointer:]

    # Mutators
    def append_news(self, news: News) -> None:
        if len(self.news_list) == self.max_capacity:
            self.news_list.pop(0)
            self.read_pointer = max(self.read_pointer - 1, 0)

        self.news_list.append(news)

if __name__ == "__main__":
    pass