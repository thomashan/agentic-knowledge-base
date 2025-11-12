from typing import Any

import requests
from agents_core.core import AbstractTool


class OutlineTool(AbstractTool):
    """
    A tool for interacting with the Outline API.
    """

    def __init__(self, api_key: str, base_url: str):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @property
    def name(self) -> str:
        """The unique name of the tool."""
        return "Outline Document Tool"

    @property
    def description(self) -> str:
        """A clear description of what the tool does and its parameters."""
        return "A tool to create, update, and manage documents in an Outline knowledge base."

    def execute(self, **kwargs: Any) -> Any:
        """
        Executes a command on the Outline knowledge base.

        Args:
            command (str): The command to execute (e.g., 'create_or_update_document').
            **kwargs: Arguments for the command.

        Returns:
            The result of the command execution.
        """
        command = kwargs.get("command")
        if not command:
            raise ValueError("A 'command' argument must be provided to execute.")

        if command == "create_or_update_document":
            title = kwargs.get("title")
            content = kwargs.get("content")
            if not title or not content:
                raise ValueError("'title' and 'content' are required for create_or_update_document.")
            return self.create_or_update_document(title=title, content=content)
        else:
            raise ValueError(f"Unknown command: {command}")

    def search_document(self, query: str) -> str | None:
        """
        Searches for a document by title and returns the first match's ID.
        """
        search_url = f"{self._base_url}/api/documents.search"
        payload = {"query": query}
        response = requests.post(search_url, headers=self._headers, json=payload)
        response.raise_for_status()
        results = response.json().get("data", [])

        if not results:
            return None

        # Assuming the first result is the most relevant one
        return results[0].get("document", {}).get("id")

    def _handle_api_response(self, response: requests.Response) -> str:
        """Handles the API response, raising for status and returning the URL."""
        response.raise_for_status()
        response_data = response.json()
        return f"{self._base_url}{response_data['data']['url']}"

    def create_or_update_document(self, title: str, content: str, collection_id: str | None = None) -> str:
        """
        Creates a new document or updates an existing one.
        """
        existing_doc_id = self.search_document(title)

        if existing_doc_id:
            # Update existing document
            url = f"{self._base_url}/api/documents.update"
            payload = {
                "id": existing_doc_id,
                "title": title,
                "text": content,
            }
        else:
            # Create a new document
            url = f"{self._base_url}/api/documents.create"
            payload = {
                "title": title,
                "text": content,
            }
            if collection_id:
                payload["collectionId"] = collection_id

        response = requests.post(url, headers=self._headers, json=payload)
        return self._handle_api_response(response)
