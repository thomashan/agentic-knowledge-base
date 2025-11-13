from abc import ABC, abstractmethod


class DocumentationTool(ABC):
    @abstractmethod
    def create_or_update_document(self, title: str, content: str) -> dict:
        """
        Creates a new document or updates an existing one in the documentation platform.
        """
        pass
