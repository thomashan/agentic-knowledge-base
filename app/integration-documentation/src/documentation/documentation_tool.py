from abc import abstractmethod
from typing import Any

from agents_core.core import AbstractTool


class DocumentationTool(AbstractTool):
    """
    Abstract base class for a documentation tool, combining the AbstractTool
    interface with methods specific to documentation platforms.
    """

    @property
    def name(self) -> str:
        return "Documentation Tool"

    @property
    def description(self) -> str:
        return "A tool for creating, updating, and managing documents."

    @abstractmethod
    def create_or_update_document(self, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
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

    def execute(self, **kwargs: Any) -> Any:
        """
        Executes a command on the documentation tool.
        This provides a generic interface for agents that use AbstractTool.
        """
        command = kwargs.pop("command", None)
        if not command:
            raise ValueError("A 'command' argument must be provided to execute.")

        if command == "create_or_update_document":
            return self.create_or_update_document(**kwargs)
        elif command == "publish_document":
            return self.publish_document(**kwargs)
        elif command == "update_document":
            return self.update_document(**kwargs)
        elif command == "get_document":
            return self.get_document(**kwargs)
        elif command == "delete_document":
            return self.delete_document(**kwargs)
        else:
            raise ValueError(f"Unknown command: {command}")
