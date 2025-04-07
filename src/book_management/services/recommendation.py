import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationService:
    @staticmethod
    def get_recommendations(target_text: str, texts: list[str], book_ids: list[int], limit: int) -> list[int]:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        target_vector = vectorizer.transform([target_text])

        similarities = cosine_similarity(target_vector, tfidf_matrix).flatten()

        similar_indices = np.argsort(similarities)[::-1]
        similar_indices = [index for index in similar_indices if book_ids[index] != book_ids[texts.index(target_text)]][
            :limit
        ]

        return [book_ids[index] for index in similar_indices]
