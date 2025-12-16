from abc import abstractmethod
from typing import Any

from agents_core.core import AbstractTool
from pydantic import BaseModel, Field


class CreateCollectionArgs(BaseModel):
    """Arguments for the create_collection command."""

    collection_name: str = Field(..., description="The name of the collection.")
    vector_size: int = Field(..., description="The size of the vectors.")
    distance: str = Field("Cosine", description="The distance metric to use (Cosine, Euclid, Dot).")


class ListCollectionsArgs(BaseModel):
    """Arguments for the list_collections command."""

    pass


class GetCollectionInfoArgs(BaseModel):
    """Arguments for the get_collection_info command."""

    collection_name: str = Field(..., description="The name of the collection to inspect.")


class DeleteCollectionArgs(BaseModel):
    """Arguments for the delete_collection command."""

    collection_name: str = Field(..., description="The name of the collection to delete.")


class UpsertVectorsArgs(BaseModel):
    """Arguments for the upsert_vectors command."""

    collection_name: str = Field(..., description="The name of the collection.")
    vectors: list[list[float]] = Field(..., description="The vectors to upsert.")
    payloads: list[dict] = Field(..., description="The payloads to upsert.")
    ids: list[str] = Field(..., description="The IDs of the vectors.")


class DeleteVectorsArgs(BaseModel):
    """Arguments for the delete_vectors command."""

    collection_name: str = Field(..., description="The name of the collection.")
    ids: list[str] = Field(..., description="The IDs of the vectors to delete.")


class SearchVectorsArgs(BaseModel):
    """Arguments for the search_vectors command."""

    collection_name: str = Field(..., description="The name of the collection.")
    query_vector: list[float] = Field(..., description="The vector to search for.")
    limit: int = Field(..., description="The maximum number of results to return.")
    with_payload: bool = Field(True, description="Whether to include the payload in the search results.")


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

    def get_command_schemas(self) -> dict[str, type[BaseModel]] | None:
        return {
            "create_collection": CreateCollectionArgs,
            "list_collections": ListCollectionsArgs,
            "get_collection_info": GetCollectionInfoArgs,
            "delete_collection": DeleteCollectionArgs,
            "upsert_vectors": UpsertVectorsArgs,
            "delete_vectors": DeleteVectorsArgs,
            "search_vectors": SearchVectorsArgs,
        }
