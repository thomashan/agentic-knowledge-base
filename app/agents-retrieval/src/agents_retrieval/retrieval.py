from sentence_transformers import SentenceTransformer
from vectordb_qdrant.qdrant_tool import QdrantTool

from agents_retrieval.models import RetrievalResult, RetrievedChunk


class RetrievalAgent:
    def __init__(self, embedding_model: SentenceTransformer, vectordb_tool: QdrantTool, collection_name: str):
        self.embedding_model = embedding_model
        self.vectordb_tool = vectordb_tool
        self.collection_name = collection_name

    def retrieve(self, query: str, limit: int = 5) -> RetrievalResult:
        # Generate query embedding
        query_vector = self.embedding_model.encode(query).tolist()

        # Search Qdrant
        search_results_dicts = self.vectordb_tool.execute(
            "search",
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )

        # Process search results into RetrievedChunk models
        retrieved_chunks = []
        for item in search_results_dicts:
            payload = item.get("payload", {})
            retrieved_chunks.append(
                RetrievedChunk(
                    document_url=payload.get("document_url", ""),
                    text=payload.get("text", ""),
                    score=item.get("score", 0.0),
                    metadata=payload,
                )
            )

        return RetrievalResult(query=query, retrieved_chunks=retrieved_chunks)
