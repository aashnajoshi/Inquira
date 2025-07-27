from embedding import Embedder
from vector_store import VectorStore

class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k=5):
        query_emb = self.embedder.embed_texts([query])[0]
        results = self.vector_store.search(query_emb, top_k=top_k)
        return results