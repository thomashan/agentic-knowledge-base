import uuid
from unittest.mock import MagicMock, patch

import pytest
from qdrant_client.http import models
from vectordb_qdrant.qdrant_tool import QdrantTool


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


def test_create_collection_new(tool, mock_qdrant_client):
    """
    Tests creating a new collection when it doesn't exist.
    """
    collection_name = "new_col"
    vector_size = 128
    distance = "Dot"

    mock_qdrant_client.collection_exists.return_value = False

    result = tool.create_collection(collection_name, vector_size, distance)

    mock_qdrant_client.delete_collection.assert_not_called()
    mock_qdrant_client.create_collection.assert_called_once_with(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.DOT),
    )
    assert f"Collection '{collection_name}' created successfully." in result


def test_create_collection_overwrite(tool, mock_qdrant_client):
    """
    Tests creating a collection that already exists (overwrite behavior).
    """
    collection_name = "existing_col"
    vector_size = 128
    distance = "Dot"

    mock_qdrant_client.collection_exists.return_value = True

    result = tool.create_collection(collection_name, vector_size, distance)

    mock_qdrant_client.delete_collection.assert_called_once_with(collection_name)
    mock_qdrant_client.create_collection.assert_called_once_with(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.DOT),
    )
    assert f"Collection '{collection_name}' created successfully." in result


def test_list_collections(tool, mock_qdrant_client):
    """
    Tests listing collections.
    """
    c1 = MagicMock()
    c1.name = "c1"
    c2 = MagicMock()
    c2.name = "c2"
    mock_qdrant_client.get_collections.return_value.collections = [c1, c2]

    result = tool.list_collections()

    assert result == ["c1", "c2"]


def test_get_collection_info(tool, mock_qdrant_client):
    """
    Tests getting collection info.
    """
    collection_name = "info_col"
    mock_info = MagicMock()
    mock_info.status = "green"
    mock_info.config.params.vectors.size = 100
    mock_info.config.params.vectors.distance = "Cosine"
    mock_info.points_count = 500
    mock_qdrant_client.get_collection.return_value = mock_info

    result = tool.get_collection_info(collection_name)

    assert result["status"] == "green"
    assert result["vector_size"] == 100
    assert result["distance"] == "Cosine"
    assert result["points_count"] == 500


def test_delete_collection(tool, mock_qdrant_client):
    """
    Tests deleting a collection.
    """
    collection_name = "del_col"
    result = tool.delete_collection(collection_name)

    mock_qdrant_client.delete_collection.assert_called_once_with(collection_name=collection_name)
    assert f"Collection '{collection_name}' deleted successfully." in result


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


def test_delete_vectors(tool, mock_qdrant_client):
    """
    Tests that the delete_vectors method calls the client's delete method correctly.
    """
    collection_name = "test_collection"
    ids = ["id1", "id2", "id3"]

    # Mock the return value for the delete operation if necessary, though it often returns None or a success status
    mock_qdrant_client.delete.return_value = {"status": "ok"}  # Example return value

    tool.delete_vectors(collection_name=collection_name, ids=ids)

    from qdrant_client.http import models

    # Assert that the Qdrant client's delete method was called once with the correct arguments
    mock_qdrant_client.delete.assert_called_once_with(collection_name=collection_name, points_selector=models.PointIdsList(points=ids), wait=True)


def test_search_vectors(tool, mock_qdrant_client):
    """
    Tests that the search_vectors method calls the client's query_points method correctly.
    """
    collection_name = "test_collection_search"
    query_vector = [0.7, 0.8, 0.9]
    limit = 15

    tool.search_vectors(collection_name=collection_name, query_vector=query_vector, limit=limit)

    mock_qdrant_client.query_points.assert_called_once_with(collection_name=collection_name, query=query_vector, limit=limit, with_payload=True)


def test_execute_dispatches_to_upsert(tool, mock_qdrant_client):
    """
    Tests that the main execute method dispatches to the upsert_vectors method and returns the result.
    """
    expected_ids = ["id1"]
    # Mock the underlying client method that upsert_vectors calls
    mock_qdrant_client.upsert.return_value = MagicMock()

    kwargs = {"command": "upsert_vectors", "collection_name": "a_collection", "vectors": [[1.0]], "payloads": [{}], "ids": expected_ids}
    result = tool.execute(**kwargs)
    mock_qdrant_client.upsert.assert_called_once()
    assert result == expected_ids


def test_execute_dispatches_to_delete(tool, mock_qdrant_client):
    """
    Tests that the main execute method dispatches to the delete_vectors method and returns the result.
    """
    expected_result = ["del_id1", "del_id2"]  # delete_vectors returns the deleted IDs
    # Mock the underlying client method that delete_vectors calls
    mock_qdrant_client.delete.return_value = MagicMock()  # Mock the client's delete operation

    collection_name = "test_collection_to_delete"
    ids = ["del_id1", "del_id2"]
    kwargs = {"command": "delete_vectors", "collection_name": collection_name, "ids": ids}

    result = tool.execute(**kwargs)

    mock_qdrant_client.delete.assert_called_once()
    assert result == expected_result


def test_execute_dispatches_to_search(tool, mock_qdrant_client):
    """
    Tests that the main execute method dispatches to the search_vectors method.
    """
    expected_search_results = []
    # Mock the underlying client method that search_vectors calls
    mock_qdrant_client.query_points.return_value = MagicMock(points=[])

    kwargs = {"command": "search_vectors", "collection_name": "a_collection", "query_vector": [0.1], "limit": 5}
    result = tool.execute(**kwargs)
    mock_qdrant_client.query_points.assert_called_once()
    assert result == expected_search_results


def test_execute_dispatches_to_create_collection(tool, mock_qdrant_client):
    """
    Tests that the main execute method dispatches to the create_collection method.
    """
    collection_name = "new_collection"
    vector_size = 128
    distance = "Dot"

    # Mock the underlying client method that create_collection calls
    mock_qdrant_client.collection_exists.return_value = False
    mock_qdrant_client.create_collection.return_value = None

    kwargs = {"command": "create_collection", "collection_name": collection_name, "vector_size": vector_size, "distance": distance}
    result = tool.execute(**kwargs)

    mock_qdrant_client.create_collection.assert_called_once()
    assert result == f"Collection '{collection_name}' created successfully."


def test_execute_dispatches_to_list_collections(tool, mock_qdrant_client):
    """
    Tests that the main execute method dispatches to the list_collections method.
    """
    mock_collections_response = MagicMock()
    mock_col1 = MagicMock()
    mock_col1.name = "col1"
    mock_col2 = MagicMock()
    mock_col2.name = "col2"
    mock_collections_response.collections = [mock_col1, mock_col2]
    mock_qdrant_client.get_collections.return_value = mock_collections_response

    kwargs = {"command": "list_collections"}
    result = tool.execute(**kwargs)

    mock_qdrant_client.get_collections.assert_called_once()
    assert result == ["col1", "col2"]


def test_execute_dispatches_to_get_collection_info(tool, mock_qdrant_client):
    """
    Tests that the main execute method dispatches to the get_collection_info method.
    """
    collection_name = "test_info_collection"
    mock_info_response = MagicMock()
    mock_info_response.status = "green"
    mock_info_response.config.params.vectors.size = 1536
    mock_info_response.config.params.vectors.distance = "Cosine"
    mock_info_response.points_count = 100

    mock_qdrant_client.get_collection.return_value = mock_info_response

    kwargs = {"command": "get_collection_info", "collection_name": collection_name}
    result = tool.execute(**kwargs)

    mock_qdrant_client.get_collection.assert_called_once_with(collection_name)
    assert result == {
        "status": "green",
        "vector_size": 1536,
        "distance": "Cosine",
        "points_count": 100,
    }


def test_execute_dispatches_to_delete_collection(tool, mock_qdrant_client):
    """
    Tests that the main execute method dispatches to the delete_collection method.
    """
    collection_name = "collection_to_delete"
    mock_qdrant_client.delete_collection.return_value = None

    kwargs = {"command": "delete_collection", "collection_name": collection_name}
    result = tool.execute(**kwargs)

    mock_qdrant_client.delete_collection.assert_called_once_with(collection_name=collection_name)
    assert result == f"Collection '{collection_name}' deleted successfully."


if __name__ == "__main__":
    pytest.main([__file__])
