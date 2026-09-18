from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.indexing.embeddings import EmbeddingService


QDRANT_PATH = "./qdrant_data"


class VectorStore:
    def __init__(self, collection_name: str = "code_units"):
        self.embeddings = EmbeddingService()
        self.client = QdrantClient(path=QDRANT_PATH)
        self.collection_name = collection_name
        self.store = None

    def add_documents(self, documents: list[Document]) -> None:
        """Add documents to the vector store."""

        if not self.client.collection_exists(self.collection_name):
            vector_size = len(
                self.embeddings.embed_query("test")
            )

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

        if self.store is None:
            self.store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings.model,
            )

        self.store.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 5,
    ):
        if self.store is None:
            self.store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings.model,
            )

        return self.store.similarity_search_with_score(query, k=k)