from abc import abstractmethod
from typing import Any

from agents_core.core import AbstractTool


class VectorDBTool(AbstractTool):
    """
    A tool for interacting with a vector database.
    """

    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int, distance: str = "Cosine") -> str:
        pass

    @abstractmethod
    def list_collections(self) -> list[str]:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> str:
        pass

    @abstractmethod
    def upsert_vectors(self, collection_name: str, vectors: list[list[float]], payloads: list[dict[str, Any]], ids: list[str]) -> list[str]:
        pass

    @abstractmethod
    def delete_vectors(self, collection_name: str, ids: list[str]) -> list[str]:
        pass

    @abstractmethod
    def search_vectors(self, collection_name: str, query_vector: list[float], limit: int, with_payload: bool = True) -> list[dict[str, Any]]:
        pass
