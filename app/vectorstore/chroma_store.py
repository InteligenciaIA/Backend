from __future__ import annotations

import chromadb
from chromadb.api.models.Collection import Collection


class ChromaVectorStore:
    def __init__(self, persist_directory: str, collection_name: str) -> None:
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name, metadata={'hnsw:space': 'cosine'})

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(name=self.collection_name, metadata={'hnsw:space': 'cosine'})

    def add(self, ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        self.collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    def query(self, query_embedding: list[float], top_k: int) -> dict:
        return self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

    def count(self) -> int:
        return self.collection.count()
