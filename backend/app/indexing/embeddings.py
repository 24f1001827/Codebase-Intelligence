from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingService:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    
    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """
        Embed a list of documents.
        """
        return self.model.embed_documents(documents)
    
    def embed_query(self, query: str) -> list[float]:
        """
        Embed a query.
        """
        return self.model.embed_query(query)