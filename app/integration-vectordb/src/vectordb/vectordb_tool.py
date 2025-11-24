from abc import abstractmethod
from typing import Any

from agents_core.core import AbstractTool


class VectorDBTool(AbstractTool):
    """
    A tool for interacting with a vector database.
    """

    @abstractmethod
    def upsert_vectors(self, collection_name: str, vectors: list[list[float]], payloads: list[dict[str, Any]], ids: list[str]) -> list[str]:
        pass

    @abstractmethod
    def delete_vectors(self, collection_name: str, ids: list[str]) -> list[str]:
        pass

    @abstractmethod
    def search_vectors(self, collection_name: str, query_vector: list[float], limit: int, with_payload: bool = True) -> list[dict[str, Any]]:
        pass
