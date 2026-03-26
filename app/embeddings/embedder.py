from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def encode_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()
