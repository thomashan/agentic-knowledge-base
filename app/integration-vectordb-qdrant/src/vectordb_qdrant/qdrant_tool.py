from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from vectordb.vectordb_tool import VectorDBTool


class QdrantTool(VectorDBTool):
    """
    A tool for interacting with a Qdrant vector database.
    """

    def __init__(self, host: str, grpc_port: int, http_port: int):
        self._client = QdrantClient(host=host, grpc_port=grpc_port, port=http_port)
        self._command_methods = {
            "create_collection": self.create_collection,
            "list_collections": self.list_collections,
            "get_collection_info": self.get_collection_info,
            "delete_collection": self.delete_collection,
            "upsert_vectors": self.upsert_vectors,
            "delete_vectors": self.delete_vectors,
            "search_vectors": self.search_vectors,
        }

    @property
    def name(self) -> str:
        """The unique name of the tool."""
        return "Qdrant VectorDB Tool"

    @property
    def description(self) -> str:
        """A clear description of what the tool does and its parameters."""
        return (
            "A tool to create, update, and query vector collections in a Qdrant database."
            "To use the tool, you must provide a `command` argument."
            "Available commands are:"
            "- `create_collection`: Creates a new collection. Requires `collection_name`, `vector_size`, and optional `distance`."
            "- `list_collections`: Lists all collection names."
            "- `get_collection_info`: Gets info about a collection. Requires `collection_name`."
            "- `delete_collection`: Deletes a collection. Requires `collection_name`."
            "- `upsert_vectors`: Upserts vectors into a collection. Requires `collection_name`, `vectors`, `payloads`, and `ids`."
            "- `delete_vectors`: Deletes vectors from a collection. Requires `collection_name` and `ids`."
            "- `search_vectors`: Searches for vectors in a collection. Requires `collection_name`, `query_vector`, and `limit`."
        )

    def execute(self, **kwargs: Any) -> Any:
        """
        Executes a command on the Qdrant vector database.

        Args:
            command (str): The command to execute (e.g., 'upsert_vectors').
            **kwargs: Arguments for the command.

        Returns:
            The result of the command execution.
        """
        import inspect

        command = kwargs.pop("command", None)
        if not command:
            raise ValueError("A 'command' argument must be provided to execute.")

        method = self._command_methods.get(command)
        if not method:
            raise ValueError(f"Unknown command: {command}")

        # Filter kwargs to only include arguments accepted by the method
        sig = inspect.signature(method)
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

        return method(**filtered_kwargs)

    def create_collection(self, collection_name: str, vector_size: int, distance: str = "Cosine") -> str:
        """
        Creates a new collection in Qdrant.
        """
        distance_map = {
            "Cosine": models.Distance.COSINE,
            "Euclid": models.Distance.EUCLID,
            "Dot": models.Distance.DOT,
        }

        # Default to Cosine if invalid distance provided
        metric = distance_map.get(distance, models.Distance.COSINE)

        if self._client.collection_exists(collection_name):
            self._client.delete_collection(collection_name)

        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=metric),
        )
        return f"Collection '{collection_name}' created successfully."

    def list_collections(self) -> list[str]:
        """
        Lists all collection names in Qdrant.
        """
        result = self._client.get_collections()
        return [c.name for c in result.collections]

    def get_collection_info(self, collection_name: str) -> dict[str, Any]:
        """
        Returns configuration info (vector size, distance) for a collection.
        """
        info = self._client.get_collection(collection_name)
        # Flatten structure for easier LLM consumption
        return {
            "status": str(info.status),
            "vector_size": info.config.params.vectors.size,
            "distance": str(info.config.params.vectors.distance),
            "points_count": info.points_count,
        }

    def delete_collection(self, collection_name: str) -> str:
        """
        Deletes a collection from Qdrant.
        """
        self._client.delete_collection(collection_name=collection_name)
        return f"Collection '{collection_name}' deleted successfully."

    def upsert_vectors(self, collection_name: str, vectors: list[list[float]], payloads: list[dict], ids: list[str]) -> list[str]:
        """
        Upserts vectors into a Qdrant collection.
        """
        points = [PointStruct(id=point_id, vector=vector, payload=payload) for point_id, vector, payload in zip(ids, vectors, payloads, strict=False)]
        self._client.upsert(collection_name=collection_name, points=points, wait=True)
        return ids

    def delete_vectors(self, collection_name: str, ids: list[str]) -> list[str]:
        """
        Deletes vectors from a Qdrant collection by their IDs.
        """
        self._client.delete(collection_name=collection_name, points_selector=models.PointIdsList(points=ids), wait=True)
        return ids

    def search_vectors(self, collection_name: str, query_vector: list[float], limit: int, with_payload: bool = True) -> list[dict[str, Any]]:
        """
        Searches for vectors in a Qdrant collection.
        """
        search_result = self._client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            with_payload=with_payload,
        )
        # Transform ScoredPoint objects to generic dictionaries
        transformed_results = []
        for scored_point in search_result.points:
            transformed_results.append(
                {
                    "id": scored_point.id,
                    "score": scored_point.score,
                    "payload": scored_point.payload,
                    "vector": scored_point.vector,
                }
            )
        return transformed_results
