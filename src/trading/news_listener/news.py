import datetime
import re

class News:
    def __init__(self, headline: str, article_link: str, description: str, 
        timestamp: datetime.datetime = None) -> None:

        if timestamp is None:
            timestamp = datetime.datetime.now()

        self.headline = headline
        self.article_link = article_link
        self.description = description
        self.timestamp = timestamp

    def as_telegram_message(self) -> str:
        return re.sub( # Remove non ASCII characters
            r"[^\x00-\x7F]", '',
            f"<b>{self.headline}</b>\r{self.timestamp.strftime(r'%b %d, %Y %I:%M %p')} GMT\r" \
                + f"{self.article_link}\r\r{self.description}"
        )

if __name__ == "__main__":
    pass