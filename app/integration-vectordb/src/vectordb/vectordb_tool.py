from agents_core.core import AbstractTool


class VectorDBTool(AbstractTool):
    """
    A tool for interacting with a vector database.
    """

    def upsert_vectors(self, collection_name: str, vectors: list[list[float]], payloads: list[dict], ids: list[str]) -> list[str]:
        pass

    def delete_vectors(self, collection_name: str, ids: list[str]) -> list[str]:
        pass
