import pytest
from agents_retrieval.models import RetrievalResult, RetrievedChunk
from pydantic import ValidationError


def test_retrieved_chunk_model_validation():
    """
    Tests the validation of the RetrievedChunk Pydantic model.
    This test will fail until the RetrievedChunk model is implemented.
    """
    # Test valid data
    valid_chunk_data = {
        "document_url": "http://example.com/doc1",
        "text": "This is a relevant text chunk.",
        "score": 0.95,
        "metadata": {"source": "doc1", "page": 3},
    }
    # This will raise a NameError until RetrievedChunk is defined
    chunk = RetrievedChunk(**valid_chunk_data)
    assert chunk.document_url == "http://example.com/doc1"
    assert chunk.text == "This is a relevant text chunk."
    assert chunk.score == 0.95
    assert chunk.metadata == {"source": "doc1", "page": 3}

    # Test missing required fields
    with pytest.raises(ValidationError):
        RetrievedChunk(document_url="http://example.com/doc1", text="text", score=0.8)  # Missing metadata

    with pytest.raises(ValidationError):
        RetrievedChunk(text="text", score=0.8, metadata={})  # Missing document_url

    # Test invalid types
    with pytest.raises(ValidationError):
        RetrievedChunk(document_url=123, text="text", score=0.8, metadata={})

    with pytest.raises(ValidationError):
        RetrievedChunk(document_url="url", text="text", score="high", metadata={})


def test_retrieval_result_model_validation():
    """
    Tests the validation of the RetrievalResult Pydantic model.
    This test will fail until the RetrievalResult model is implemented.
    """
    # Test valid data
    valid_result_data = {
        "query": "What is the capital of France?",
        "retrieved_chunks": [
            {
                "document_url": "http://example.com/doc1",
                "text": "Paris is the capital of France.",
                "score": 0.99,
                "metadata": {"source": "wiki"},
            },
            {
                "document_url": "http://example.com/doc2",
                "text": "France is a country in Europe.",
                "score": 0.85,
                "metadata": {"source": "geo"},
            },
        ],
    }
    # This will raise a NameError until RetrievalResult is defined
    result = RetrievalResult(**valid_result_data)
    assert result.query == "What is the capital of France?"
    assert len(result.retrieved_chunks) == 2
    assert result.retrieved_chunks[0].text == "Paris is the capital of France."

    # Test missing required fields
    with pytest.raises(ValidationError):
        RetrievalResult(query="test")  # Missing retrieved_chunks

    # Test invalid types
    with pytest.raises(ValidationError):
        RetrievalResult(query=123, retrieved_chunks=[])

    with pytest.raises(ValidationError):
        RetrievalResult(query="test", retrieved_chunks="not a list")


if __name__ == "__main__":
    pytest.main([__file__])
