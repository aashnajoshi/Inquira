import faiss
import numpy as np
from langchain.vectorstores import FAISS

class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.embeddings = []

    def add(self, embeddings: list[np.array], docs: list[dict]):
        embeddings = np.array(embeddings).astype('float32')
        self.index.add(embeddings)
        self.embeddings.extend(embeddings)
        self.documents.extend(docs)

    def search(self, query_embedding: np.array, top_k=5):
        D, I = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        return [self.documents[i] for i in I[0]]

    def get_documents_with_embeddings(self):
        return list(zip(self.documents, self.embeddings))
