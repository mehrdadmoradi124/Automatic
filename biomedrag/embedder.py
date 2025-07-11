from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer


class Embedder:
    """TF-IDF based text embedder."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")

    def fit_transform(self, texts: List[str]):
        return self.vectorizer.fit_transform(texts).toarray()

    def transform(self, texts: List[str]):
        return self.vectorizer.transform(texts).toarray()
