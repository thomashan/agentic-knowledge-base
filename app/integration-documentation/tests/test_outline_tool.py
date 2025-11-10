from unittest.mock import MagicMock, patch

import pytest
from integration_documentation.outline_tool import OutlineTool


@pytest.fixture
def tool():
    """Fixture to create an OutlineTool instance."""
    return OutlineTool(api_key="test_key", base_url="http://test.com")


def test_outline_tool_instantiation(tool):
    """
    Tests that the OutlineTool can be instantiated.
    """
    assert tool is not None
    assert tool.name == "Outline Document Tool"


@patch("requests.post")
def test_create_or_update_document_creates_new_document(mock_post, tool):
    """
    Tests that a new document is created when one with the given title does not exist.
    """
    tool.search_document = MagicMock(return_value=None)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"url": "/doc/new-doc-slug"}}
    mock_post.return_value = mock_response

    result_url = tool.create_or_update_document(title="Test Title", content="Test Content")

    tool.search_document.assert_called_once_with("Test Title")
    mock_post.assert_called_once_with(f"{tool._base_url}/api/documents.create", headers=tool._headers, json={"title": "Test Title", "text": "Test Content"})
    assert result_url == "http://test.com/doc/new-doc-slug"


@patch("requests.post")
def test_create_or_update_document_updates_existing_document(mock_post, tool):
    """
    Tests that an existing document is updated when one with the given title exists.
    """
    existing_doc_id = "doc-id-abc"
    tool.search_document = MagicMock(return_value=existing_doc_id)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"url": "/doc/existing-doc-slug"}}
    mock_post.return_value = mock_response

    result_url = tool.create_or_update_document(title="Existing Title", content="Updated Content")

    tool.search_document.assert_called_once_with("Existing Title")
    mock_post.assert_called_once_with(f"{tool._base_url}/api/documents.update", headers=tool._headers, json={"id": existing_doc_id, "title": "Existing Title", "text": "Updated Content"})
    assert result_url == "http://test.com/doc/existing-doc-slug"


def test_execute_dispatches_to_create_or_update(tool):
    """
    Tests that the main execute method dispatches to the correct internal method.
    """
    tool.create_or_update_document = MagicMock(return_value="mock_url")

    result = tool.execute(command="create_or_update_document", title="A Title", content="Some Content")

    tool.create_or_update_document.assert_called_once_with(title="A Title", content="Some Content")
    assert result == "mock_url"


@patch("requests.post")
def test_search_document_found(mock_post, tool):
    """
    Tests that search_document returns a document ID when a document is found.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"document": {"id": "doc-id-123", "title": "Test Title"}}]}
    mock_post.return_value = mock_response

    doc_id = tool.search_document(query="Test Title")

    mock_post.assert_called_once_with(f"{tool._base_url}/api/documents.search", headers=tool._headers, json={"query": "Test Title"})
    assert doc_id == "doc-id-123"


@patch("requests.post")
def test_search_document_not_found(mock_post, tool):
    """
    Tests that search_document returns None when no document is found.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}
    mock_post.return_value = mock_response

    doc_id = tool.search_document(query="Non-existent Title")

    assert doc_id is None
