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
    return QdrantTool(host="localhost", port=6333)


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


if __name__ == "__main__":
    pytest.main()
