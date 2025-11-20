"""
Unit tests for the OutlineTool class.
"""

from unittest.mock import MagicMock, patch

import pytest
from documentation.documentation_tool import DocumentationTool
from documentation.outline_tool import OutlineTool


@pytest.fixture
def outline_tool():
    """Fixture to create an OutlineTool instance for testing."""
    return OutlineTool(api_key="test_api_key", base_url="http://fake-outline.com", collection_id="test_collection_id")


def test_outline_tool_is_documentation_tool(outline_tool):
    """Verify that OutlineTool is a subclass of DocumentationTool."""
    assert isinstance(outline_tool, DocumentationTool)


def test_headers_include_accept(outline_tool):
    """Verify that the headers include the 'Accept' header."""
    assert "Accept" in outline_tool.headers
    assert outline_tool.headers["Accept"] == "application/json"


def test_base_url_stripping():
    """Verify that trailing slashes are stripped from the base_url."""
    tool = OutlineTool(api_key="test_key", base_url="https://test.com/", collection_id="test_collection_id")
    assert tool.base_url == "https://test.com"


@patch("requests.post")
def test_publish_document(mock_post, outline_tool):
    """Test publishing a new document."""
    # Arrange
    mock_response = MagicMock()
    expected_response_json = {"data": {"id": "new_doc_id", "title": "Test Title"}}
    mock_response.json.return_value = expected_response_json
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    title = "Test Title"
    content = "Test Content"

    # Act
    result = outline_tool.publish_document(title, content)

    # Assert
    mock_post.assert_called_once_with(
        f"{outline_tool.base_url}/api/documents.create",
        headers=outline_tool.headers,
        json={
            "title": title,
            "text": content,
            "publish": True,
            "collectionId": outline_tool.collection_id,
        },
    )
    assert result == expected_response_json


@patch("requests.post")
def test_get_document(mock_post, outline_tool):
    """Test retrieving a document."""
    # Arrange
    mock_response = MagicMock()
    expected_response_json = {"data": {"id": "doc_to_get", "title": "Test Get"}}
    mock_response.json.return_value = expected_response_json
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    doc_id = "doc_to_get"

    # Act
    result = outline_tool.get_document(doc_id)

    # Assert
    mock_post.assert_called_once_with(
        f"{outline_tool.base_url}/api/documents.info",
        headers=outline_tool.headers,
        json={"id": doc_id},
    )
    assert result == expected_response_json


@patch("requests.post")
def test_update_document(mock_post, outline_tool):
    """Test updating an existing document."""
    # Arrange
    mock_response = MagicMock()
    expected_response_json = {"data": {"id": "doc_to_update", "title": "New Title"}}
    mock_response.json.return_value = expected_response_json
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    doc_id = "doc_to_update"
    title = "New Title"
    content = "New Content"

    # Act
    result = outline_tool.update_document(doc_id, title, content)

    # Assert
    mock_post.assert_called_once_with(
        f"{outline_tool.base_url}/api/documents.update",
        headers=outline_tool.headers,
        json={
            "id": doc_id,
            "title": title,
            "text": content,
        },
    )
    assert result == expected_response_json


@patch("requests.post")
def test_delete_document(mock_post, outline_tool):
    """Test deleting a document."""
    # Arrange
    mock_response = MagicMock()
    # The documents.delete API returns a simple `{"success": true}`
    expected_response_json = {"success": True}
    mock_response.json.return_value = expected_response_json
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    doc_id = "doc_to_delete"

    # Act
    result = outline_tool.delete_document(doc_id)

    # Assert
    mock_post.assert_called_once_with(
        f"{outline_tool.base_url}/api/documents.delete",
        headers=outline_tool.headers,
        json={"id": doc_id, "permanent": False},
    )
    assert result is True


@patch.object(OutlineTool, "publish_document", return_value={"data": {"id": "new-doc", "title": "New Document"}})
@patch.object(OutlineTool, "_search_document_by_title", return_value=None)
def test_create_or_update_document_creates_new(mock_search, mock_publish, outline_tool):
    """Test that a new document is created when one doesn't exist."""
    title = "New Document"
    content = "Some content"
    response = outline_tool.create_or_update_document(title, content, collection_id="new_collection")

    mock_search.assert_called_once_with(title)
    mock_publish.assert_called_once_with(title, content, collection_id="new_collection")
    assert response == {"data": {"id": "new-doc", "title": "New Document"}}


@patch.object(OutlineTool, "update_document", return_value={"data": {"id": "existing-doc", "title": "New Document"}})
@patch.object(OutlineTool, "_search_document_by_title")
def test_create_or_update_document_updates_existing(mock_search, mock_update, outline_tool):
    """Test that an existing document is updated."""
    title = "Existing Document"
    content = "Updated content"
    existing_doc_id = "existing-doc"
    mock_search.return_value = {"id": existing_doc_id}

    response = outline_tool.create_or_update_document(title, content, some_kwarg="value")

    mock_search.assert_called_once_with(title)
    mock_update.assert_called_once_with(existing_doc_id, title, content, some_kwarg="value")
    assert response == {"data": {"id": "existing-doc", "title": "New Document"}}


if __name__ == "__main__":
    pytest.main()
