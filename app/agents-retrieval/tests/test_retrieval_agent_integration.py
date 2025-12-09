from unittest.mock import MagicMock

import pytest
from agents_retrieval.models import RetrievalResult, RetrievedChunk
from agents_retrieval.retrieval import RetrievalAgent
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_tool import QdrantTool


@pytest.fixture(scope="module")
def real_embedding_model():
    """Fixture for a real embedding model."""
    return SentenceTransformer("all-MiniLM-L6-v2")


@pytest.fixture
def mock_qdrant_tool_for_integration():
    """
    Fixture for a mocked QdrantTool instance for integration testing.
    This mock will directly control the return value of its `execute` method.
    """
    mock_tool = MagicMock(spec=QdrantTool)

    # Configure the mock execute method to return realistic ScoredPoint objects
    mock_tool.execute.return_value = [
        # Simulate a ScoredPoint-like dictionary structure
        {
            "id": "doc_id_1",
            "score": 0.98,
            "payload": {
                "document_url": "https://example.com/integration_doc1",
                "text": "Integration test chunk one.",
            },
            "vector": [0.1] * 384,  # Dummy vector, length 384 for all-MiniLM-L6-v2
        },
        {
            "id": "doc_id_2",
            "score": 0.90,
            "payload": {
                "document_url": "https://example.com/integration_doc2",
                "text": "Integration test chunk two.",
            },
            "vector": [0.2] * 384,
        },
    ]

    return mock_tool


def test_retrieval_agent_integration(real_embedding_model, mock_qdrant_tool_for_integration):
    """
    Tests the full data flow of the RetrievalAgent with a real embedding model
    and a QdrantTool whose internal client is mocked.
    """
    # Arrange
    query = "integration test query"
    collection_name = "knowledge_base"
    limit = 2

    agent = RetrievalAgent(
        embedding_model=real_embedding_model,
        vectordb_tool=mock_qdrant_tool_for_integration,
        collection_name=collection_name,
    )

    # Act
    result = agent.retrieve(query, limit)

    # Assert
    # 1. Verify embedding model was called (implicitly by calling .encode() to get query_vector)
    # The actual assertion of the vector's type/content will happen when asserting the call to QdrantTool.execute

    # 2. Verify QdrantTool's execute method (and thus internal QdrantClient.search) was called
    mock_qdrant_tool_for_integration.execute.assert_called_once_with(
        "search",
        collection_name=collection_name,
        query_vector=real_embedding_model.encode(query).tolist(),
        limit=limit,
    )

    # 3. Verify the returned RetrievalResult structure and content
    assert isinstance(result, RetrievalResult)
    assert result.query == query
    assert len(result.retrieved_chunks) == limit
    assert all(isinstance(chunk, RetrievedChunk) for chunk in result.retrieved_chunks)

    # Check first chunk details
    first_chunk = result.retrieved_chunks[0]
    assert first_chunk.document_url == "https://example.com/integration_doc1"
    assert first_chunk.text == "Integration test chunk one."
    assert first_chunk.score == 0.98
    assert first_chunk.metadata == {
        "document_url": "https://example.com/integration_doc1",
        "text": "Integration test chunk one.",
    }

    # Check second chunk details
    second_chunk = result.retrieved_chunks[1]
    assert second_chunk.document_url == "https://example.com/integration_doc2"
    assert second_chunk.text == "Integration test chunk two."
    assert second_chunk.score == 0.90
    assert second_chunk.metadata == {
        "document_url": "https://example.com/integration_doc2",
        "text": "Integration test chunk two.",
    }


if __name__ == "__main__":
    pytest.main([__file__])
