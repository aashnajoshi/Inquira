from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name, device="cpu")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()