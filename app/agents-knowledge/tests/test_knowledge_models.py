import pytest
from agents_knowledge.models import DocumentChunk, KnowledgePersistenceResult
from pydantic import ValidationError


def test_document_chunk_valid():
    """Tests that a valid DocumentChunk model can be created."""
    chunk = DocumentChunk(chunk_id="doc-1-chunk-0", text="This is a text chunk.", metadata={"source": "http://example.com"})
    assert chunk.chunk_id == "doc-1-chunk-0"
    assert chunk.text == "This is a text chunk."
    assert chunk.metadata == {"source": "http://example.com"}


def test_document_chunk_invalid():
    """Tests that a DocumentChunk model raises validation errors for missing fields."""
    with pytest.raises(ValidationError):
        DocumentChunk(chunk_id="only-id")


def test_knowledge_persistence_result_valid():
    """Tests that a valid KnowledgePersistenceResult model can be created."""
    result = KnowledgePersistenceResult(document_url="http://example.com/doc/123", vector_ids=["vec-1", "vec-2"])
    assert result.document_url == "http://example.com/doc/123"
    assert result.vector_ids == ["vec-1", "vec-2"]


def test_knowledge_persistence_result_invalid():
    """Tests that a KnowledgePersistenceResult model raises validation errors for missing fields."""
    with pytest.raises(ValidationError):
        KnowledgePersistenceResult(document_url="only-url")


if __name__ == "__main__":
    pytest.main()
