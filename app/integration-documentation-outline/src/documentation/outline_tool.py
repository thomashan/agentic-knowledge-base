from typing import Any

import requests
import structlog
from documentation.documentation_tool import DocumentationTool

log = structlog.get_logger()


class OutlineTool(DocumentationTool):
    def __init__(self, api_key: str, base_url: str, collection_id: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.collection_id = collection_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @staticmethod
    def _handle_response(response: requests.Response) -> dict[str, Any]:
        response.raise_for_status()
        response_data = response.json()
        return response_data

    def _search_document_by_title(self, title: str) -> dict[str, Any] | None:
        """
        Searches for a document by title.
        Returns the document data if found, otherwise None.
        """
        search_url = f"{self.base_url}/api/documents.search"
        params = {"query": title}
        response = requests.post(search_url, headers=self.headers, json=params)
        response.raise_for_status()
        data = response.json()

        # The Outline API returns a list of documents that match the query.
        # We assume the first result is the most relevant if an exact match is not found.
        # For now, we'll look for an exact title match.
        for document in data.get("data", []):
            if document.get("document", {}).get("title") == title:
                return document.get("document")
        return None

    def update_document(self, document_id: str, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
        """
        Updates an existing document on the documentation platform and returns the response.
        """
        update_url = f"{self.base_url}/api/documents.update"
        payload = {
            "id": document_id,
            "title": title,
            "text": content,
            **kwargs,
        }
        response = requests.post(update_url, headers=self.headers, json=payload)
        return self._handle_response(response)

    def create_or_update_document(self, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
        """
        Creates a new document or updates an existing one, returning the response.
        """
        existing_document = self._search_document_by_title(title)

        if existing_document:
            document_id = existing_document["id"]
            return self.update_document(document_id, title, content, **kwargs)
        else:
            return self.publish_document(title, content, **kwargs)

    def publish_document(self, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
        """
        Publishes a document to the documentation platform and returns the response.
        """
        create_url = f"{self.base_url}/api/documents.create"
        payload = {
            "title": title,
            "text": content,
            "publish": True,
            "collectionId": self.collection_id,
            **kwargs,
        }

        response = requests.post(create_url, headers=self.headers, json=payload)
        return self._handle_response(response)

    def get_document(self, document_id: str) -> dict[str, Any]:
        """
        Retrieves a document from the documentation platform.
        Raises ValueError if the document is not found.
        """
        get_url = f"{self.base_url}/api/documents.info"
        payload = {"id": document_id}
        response = requests.post(get_url, headers=self.headers, json=payload)
        return self._handle_response(response)

    def delete_document(self, document_id: str, permanent: bool = False) -> bool:
        """
        Deletes a document from the documentation platform.
        """
        delete_url = f"{self.base_url}/api/documents.delete"
        payload = {"id": document_id, "permanent": permanent}
        response = requests.post(delete_url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json().get("success", False)
