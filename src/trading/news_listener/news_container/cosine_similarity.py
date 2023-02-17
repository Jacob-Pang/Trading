import numpy as np

from sentence_transformers import SentenceTransformer
from . import NewsContainerBase
from ..news import News

class CosineSimilarityNewsContainer (NewsContainerBase):
    def __init__(self, max_capacity: int, similarity_treshold: float = 0.8):
        NewsContainerBase.__init__(self, max_capacity, similarity_treshold)

        self.sent_transformer = SentenceTransformer("sentence-transformers/all-mpnet-base-v1")
        self.features = 768

        self.encodings = np.zeros(shape=(self.max_capacity, self.features), dtype=float)
        self.encoding_ptr = 0

    def get_encoding(self, news: News) -> np.ndarray:
        # Returns the encoded news with shape (features, ).
        return self.sent_transformer.encode([news.headline])[0]

    def get_similarity(self, news: News) -> float:
        similarity = self.encodings @ self.get_encoding(news)[:, np.newaxis]

        return np.max(similarity)

    def append_news(self, news: News) -> bool:
        if not NewsContainerBase.append_news(self, news):
            return False

        self.encodings[self.encoding_ptr, :] = self.get_encoding(news)
        self.encoding_ptr += 1
        self.encoding_ptr %= self.max_capacity
        
        return True
    
if __name__ == "__main__":
    pass