from .news import News
from .news_container import NewsContainerBase
from .news_container.cosine_similarity import CosineSimilarityNewsContainer
from ..listener import ListenerBase

class NewsListenerBase (ListenerBase):
    def __init__(self, news_container: NewsContainerBase = None) -> None:
        if not news_container:
            news_container = CosineSimilarityNewsContainer(100)

        self._news_container = news_container

    # Getters    
    def get(self) -> (News | None):
        return self._news_container.get()

    def __iter__(self):
        return self
    
    def __next__(self) -> News:
        news = self.get()

        if not news:
            raise StopIteration
        
        return news

if __name__ == "__main__":
    pass