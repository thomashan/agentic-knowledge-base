from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from vectordb.vectordb_tool import VectorDBTool


class QdrantTool(VectorDBTool):
    """
    A tool for interacting with a Qdrant vector database.
    """

    def __init__(self, host: str, grpc_port: int, http_port: int):
        self._client = QdrantClient(host=host, grpc_port=grpc_port, port=http_port)

    @property
    def name(self) -> str:
        """The unique name of the tool."""
        return "Qdrant VectorDB Tool"

    @property
    def description(self) -> str:
        """A clear description of what the tool does and its parameters."""
        return "A tool to create, update, and query vector collections in a Qdrant database."

    def execute(self, **kwargs: Any) -> Any:
        """
        Executes a command on the Qdrant vector database.

        Args:
            command (str): The command to execute (e.g., 'upsert_vectors').
            **kwargs: Arguments for the command.

        Returns:
            The result of the command execution.
        """
        command = kwargs.pop("command", None)
        if not command:
            raise ValueError("A 'command' argument must be provided to execute.")

        if command == "upsert_vectors":
            return self.upsert_vectors(**kwargs)
        elif command == "delete_vectors":
            return self.delete_vectors(**kwargs)
        else:
            raise ValueError(f"Unknown command: {command}")

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
        self._client.delete(collection_name=collection_name, points_selector=ids, wait=True)
        return ids
