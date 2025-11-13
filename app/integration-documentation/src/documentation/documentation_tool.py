from abc import ABC, abstractmethod
from typing import Any

"""
Abstract base class for documentation platform integrations.

Defines the interface that all concrete documentation platform
implementations must adhere to.
"""


class DocumentationTool(ABC):
    @abstractmethod
    def create_or_update_document(self, title: str, content: str) -> dict[str, Any]:
        """
        Creates a new document or updates an existing one in the documentation platform.
        """
        pass

    @abstractmethod
    def publish_document(self, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
        """
        Publishes a document to the documentation platform.

        Args:
            title: The title of the document.
            content: The content of the document (e.g., Markdown, HTML).
            **kwargs: Additional platform-specific parameters.

        Returns:
            A dictionary containing information about the published document,
            such as its ID, URL, etc.
        """
        pass

    @abstractmethod
    def update_document(self, document_id: str, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
        """
        Updates an existing document on the documentation platform.

        Args:
            document_id: The unique identifier of the document to update.
            title: The new title of the document.
            content: The new content of the document.
            **kwargs: Additional platform-specific parameters.

        Returns:
            A dictionary containing information about the updated document.
        """
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> dict[str, Any]:
        """
        Retrieves a document from the documentation platform.

        Args:
            document_id: The unique identifier of the document to retrieve.

        Returns:
            A dictionary containing the document's title, content, and other metadata.
        """
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """
        Deletes a document from the documentation platform.

        Args:
            document_id: The unique identifier of the document to delete.

        Returns:
            True if the document was successfully deleted, False otherwise.
        """
        pass
