from unittest.mock import MagicMock

import pytest

# Mock objects will be created for the following:
# - Embedding Model (e.g., SentenceTransformer)
# - QdrantTool (specifically its execute method)
# Test for RetrievalAgent
# This test will fail until RetrievalAgent is implemented.
# It also requires the RetrievalResult and RetrievedChunk models to be available.
from agents_retrieval.models import RetrievalResult, RetrievedChunk
from agents_retrieval.retrieval import RetrievalAgent  # Uncommented

# from qdrant_client.http.models import ScoredPoint # Not needed as we mock payload directly


@pytest.fixture
def mock_embedding_model():
    """Mock for an embedding model like SentenceTransformer."""
    mock = MagicMock()
    # Mock the encode method to return an object with a .tolist() method
    mock_encode_result = MagicMock()
    mock_encode_result.tolist.return_value = [0.1, 0.2, 0.3, 0.4]
    mock.encode.return_value = mock_encode_result
    return mock


@pytest.fixture
def mock_qdrant_tool():
    """Mock for QdrantTool."""
    mock = MagicMock()
    # Mock the execute method to return a list of sample ScoredPoint-like dicts
    mock.execute.return_value = [
        # Simulate a ScoredPoint-like dictionary structure
        {
            "id": "doc1_chunk1",
            "score": 0.95,
            "payload": {
                "document_url": "http://example.com/doc1",
                "text": "This is chunk 1 from document 1.",
            },
            "vector": [0.1, 0.2, 0.3, 0.4],
        },
        {
            "id": "doc1_chunk2",
            "score": 0.88,
            "payload": {
                "document_url": "http://example.com/doc1",
                "text": "This is chunk 2 from document 1.",
            },
            "vector": [0.1, 0.2, 0.3, 0.4],
        },
    ]
    return mock


def test_retrieval_agent_retrieve_method(mock_embedding_model, mock_qdrant_tool):
    """
    Tests the retrieve method of the RetrievalAgent.
    This test will fail until RetrievalAgent is implemented.
    """
    # Arrange
    query = "test query"
    collection_name = "knowledge_base"
    limit = 2

    # Instantiate RetrievalAgent
    agent = RetrievalAgent(
        embedding_model=mock_embedding_model,
        vectordb_tool=mock_qdrant_tool,
        collection_name=collection_name,
    )

    # Act
    result = agent.retrieve(query, limit)

    # Assert
    mock_embedding_model.encode.assert_called_once_with(query)
    mock_qdrant_tool.execute.assert_called_once_with(
        "search",  # command is passed as positional argument
        collection_name=collection_name,
        query_vector=[0.1, 0.2, 0.3, 0.4],  # Based on mock_embedding_model.encode.return_value
        limit=limit,
    )

    assert isinstance(result, RetrievalResult)
    assert result.query == query
    assert len(result.retrieved_chunks) == limit
    assert all(isinstance(chunk, RetrievedChunk) for chunk in result.retrieved_chunks)
    assert result.retrieved_chunks[0].document_url == "http://example.com/doc1"
    assert result.retrieved_chunks[0].text == "This is chunk 1 from document 1."
    assert result.retrieved_chunks[0].score == 0.95


if __name__ == "__main__":
    pytest.main()
