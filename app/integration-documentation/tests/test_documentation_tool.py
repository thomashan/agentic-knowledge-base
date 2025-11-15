"""
Tests for the core abstractions of the integration_documentation package.
"""

from typing import Any

import pytest
from documentation.documentation_tool import DocumentationTool


class ConcreteDocumentationTool(DocumentationTool):
    """
    A concrete implementation of DocumentationTool for testing purposes.
    """

    def __init__(self):
        self.published_documents = {}
        self.updated_documents = {}
        self.retrieved_documents = {}
        self.deleted_documents = {}

    def create_or_update_document(self, title: str, content: str) -> dict[str, Any]:
        # Check if a document with the same title already exists
        for doc_id, doc_data in self.published_documents.items():
            if doc_data["title"] == title:
                # Update existing document
                self.published_documents[doc_id]["content"] = content
                self.updated_documents[doc_id] = self.published_documents[doc_id]
                return {"id": doc_id, "title": title, "url": f"http://example.com/{doc_id}"}

        # Create a new document if title not found
        return self.publish_document(title, content)

    def publish_document(self, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
        doc_id = f"doc_{len(self.published_documents) + 1}"
        self.published_documents[doc_id] = {"title": title, "content": content, "kwargs": kwargs}
        return {"id": doc_id, "title": title, "url": f"http://example.com/{doc_id}"}

    def update_document(self, document_id: str, title: str, content: str, **kwargs: Any) -> dict[str, Any]:
        if document_id not in self.published_documents:
            raise ValueError(f"Document with ID {document_id} not found.")
        self.updated_documents[document_id] = {"title": title, "content": content, "kwargs": kwargs}
        self.published_documents[document_id].update({"title": title, "content": content})
        return {"id": document_id, "title": title, "url": f"http://example.com/{document_id}"}

    def get_document(self, document_id: str) -> dict[str, Any]:
        if document_id not in self.published_documents:
            raise ValueError(f"Document with ID {document_id} not found.")
        self.retrieved_documents[document_id] = self.published_documents[document_id]
        return self.published_documents[document_id]

    def delete_document(self, document_id: str) -> bool:
        if document_id in self.published_documents:
            del self.published_documents[document_id]
            self.deleted_documents[document_id] = True
            return True
        return False


def test_abstract_documentation_platform_cannot_be_instantiated():
    """
    Verify that AbstractDocumentationPlatform cannot be instantiated directly.
    """
    with pytest.raises(TypeError):
        DocumentationTool()


def test_concrete_documentation_platform_instantiation():
    """
    Verify that a concrete implementation can be instantiated.
    """
    platform = ConcreteDocumentationTool()
    assert isinstance(platform, DocumentationTool)


def test_publish_document():
    """
    Test the publish_document method of the concrete implementation.
    """
    platform = ConcreteDocumentationTool()
    title = "Test Document"
    content = "This is the content of the test document."
    result = platform.publish_document(title, content, author="Gemini")

    assert "id" in result
    assert result["title"] == title
    assert "url" in result
    assert platform.published_documents[result["id"]]["title"] == title
    assert platform.published_documents[result["id"]]["content"] == content
    assert platform.published_documents[result["id"]]["kwargs"]["author"] == "Gemini"


def test_update_document():
    """
    Test the update_document method of the concrete implementation.
    """
    platform = ConcreteDocumentationTool()
    initial_title = "Initial Document"
    initial_content = "Initial content."
    publish_result = platform.publish_document(initial_title, initial_content)
    doc_id = publish_result["id"]

    new_title = "Updated Document"
    new_content = "Updated content."
    update_result = platform.update_document(doc_id, new_title, new_content, editor="Gemini")

    assert update_result["id"] == doc_id
    assert update_result["title"] == new_title
    assert platform.published_documents[doc_id]["title"] == new_title
    assert platform.published_documents[doc_id]["content"] == new_content
    assert platform.updated_documents[doc_id]["kwargs"]["editor"] == "Gemini"


def test_update_document_not_found():
    """
    Test updating a document that does not exist.
    """
    platform = ConcreteDocumentationTool()
    with pytest.raises(ValueError, match="Document with ID non_existent_id not found."):
        platform.update_document("non_existent_id", "Title", "Content")


def test_get_document():
    """
    Test the get_document method of the concrete implementation.
    """
    platform = ConcreteDocumentationTool()
    title = "Retrievable Document"
    content = "Content to be retrieved."
    publish_result = platform.publish_document(title, content)
    doc_id = publish_result["id"]

    retrieved_doc = platform.get_document(doc_id)
    assert retrieved_doc["title"] == title
    assert retrieved_doc["content"] == content
    assert platform.retrieved_documents[doc_id]["title"] == title


def test_get_document_not_found():
    """
    Test retrieving a document that does not exist.
    """
    platform = ConcreteDocumentationTool()
    with pytest.raises(ValueError, match="Document with ID non_existent_id not found."):
        platform.get_document("non_existent_id")


def test_delete_document():
    """
    Test the delete_document method of the concrete implementation.
    """
    platform = ConcreteDocumentationTool()
    title = "Deletable Document"
    content = "Content to be deleted."
    publish_result = platform.publish_document(title, content)
    doc_id = publish_result["id"]

    assert platform.delete_document(doc_id) is True
    assert doc_id not in platform.published_documents
    assert platform.deleted_documents[doc_id] is True


def test_delete_document_not_found():
    """
    Test deleting a document that does not exist.
    """
    platform = ConcreteDocumentationTool()
    assert platform.delete_document("non_existent_id") is False


def test_create_or_update_document():
    """
    Test the create_or_update_document method for both creation and update scenarios.
    """
    platform = ConcreteDocumentationTool()
    title = "Test Create or Update"
    initial_content = "Initial content."

    # 1. Test creation
    create_result = platform.create_or_update_document(title, initial_content)
    doc_id = create_result["id"]

    assert "id" in create_result
    assert create_result["title"] == title
    assert platform.published_documents[doc_id]["content"] == initial_content

    # 2. Test update
    updated_content = "Updated content."
    update_result = platform.create_or_update_document(title, updated_content)

    # Ensure it's the same document
    assert update_result["id"] == doc_id
    assert update_result["title"] == title
    # Ensure content is updated
    assert platform.published_documents[doc_id]["content"] == updated_content
    # Ensure no new document was created
    assert len(platform.published_documents) == 1


if __name__ == "__main__":
    pytest.main()
