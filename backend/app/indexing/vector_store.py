import uuid

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

        self._ensure_collection()

        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings.model,
        )

    def _ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return

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

    def add_documents(self, documents: list[Document]) -> None:
        """Add or update documents in the vector store."""

        ids = [
            str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    document.metadata["id"],
                )
            )
            for document in documents
        ]

        self.store.add_documents(
            documents,
            ids=ids,
        )

    def similarity_search(
        self,
        query: str,
        k: int = 5,
    ):
        return self.store.similarity_search_with_score(
            query,
            k=k,
        )