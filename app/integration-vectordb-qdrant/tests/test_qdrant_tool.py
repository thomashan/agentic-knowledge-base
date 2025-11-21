import uuid
from unittest.mock import MagicMock, patch

import pytest
from vectordb.qdrant_tool import QdrantTool


@pytest.fixture
def mock_qdrant_client():
    """Fixture to mock the QdrantClient."""
    with patch("qdrant_client.QdrantClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        yield mock_client_instance


@pytest.fixture
def tool(mock_qdrant_client):
    """Fixture to create a QdrantTool instance with a mocked client."""
    qdrant_client = QdrantTool(host="localhost", grpc_port=6333, http_port=6334)
    qdrant_client._client = mock_qdrant_client
    return qdrant_client


def test_qdrant_tool_instantiation(tool, mock_qdrant_client):
    """
    Tests that the QdrantTool can be instantiated and that it initializes the client.
    """
    assert tool is not None
    assert tool.name == "Qdrant VectorDB Tool"
    # The instantiation of the client is implicitly tested by the fixture setup
    assert tool._client == mock_qdrant_client


def test_upsert_vectors(tool, mock_qdrant_client):
    """
    Tests that the upsert_vectors method calls the client's upsert method correctly and returns the ids.
    """
    collection_name = "test_collection"
    vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    payloads = [{"meta": "one"}, {"meta": "two"}]
    ids = [str(uuid.uuid4()), str(uuid.uuid4())]

    result_ids = tool.upsert_vectors(collection_name=collection_name, vectors=vectors, payloads=payloads, ids=ids)

    mock_qdrant_client.upsert.assert_called_once()
    assert result_ids == ids


def test_execute_dispatches_to_upsert(tool):
    """
    Tests that the main execute method dispatches to the upsert_vectors method and returns the result.
    """
    expected_ids = ["id1"]
    tool.upsert_vectors = MagicMock(return_value=expected_ids)
    kwargs = {"command": "upsert_vectors", "collection_name": "a_collection", "vectors": [[1.0]], "payloads": [{}], "ids": expected_ids}
    result = tool.execute(**kwargs)
    tool.upsert_vectors.assert_called_once_with(collection_name="a_collection", vectors=[[1.0]], payloads=[{}], ids=expected_ids)
    assert result == expected_ids


def test_delete_vectors(tool, mock_qdrant_client):
    """
    Tests that the delete_vectors method calls the client's delete method correctly.
    """
    collection_name = "test_collection"
    ids = ["id1", "id2", "id3"]

    # Mock the return value for the delete operation if necessary, though it often returns None or a success status
    mock_qdrant_client.delete.return_value = {"status": "ok"}  # Example return value

    tool.delete_vectors(collection_name=collection_name, ids=ids)

    # Assert that the Qdrant client's delete method was called once with the correct arguments
    mock_qdrant_client.delete.assert_called_once_with(collection_name=collection_name, points_selector=ids, wait=True)


def test_execute_dispatches_to_delete(tool):
    """
    Tests that the main execute method dispatches to the delete_vectors method and returns the result.
    """
    expected_result = {"status": "ok"}
    tool.delete_vectors = MagicMock(return_value=expected_result)
    collection_name = "test_collection_to_delete"
    ids = ["del_id1", "del_id2"]
    kwargs = {"command": "delete_vectors", "collection_name": collection_name, "ids": ids}

    result = tool.execute(**kwargs)

    tool.delete_vectors.assert_called_once_with(collection_name=collection_name, ids=ids)
    assert result == expected_result


if __name__ == "__main__":
    pytest.main()
