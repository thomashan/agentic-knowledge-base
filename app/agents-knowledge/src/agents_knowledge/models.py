from typing import Any

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Represents a single chunk of text to be vectorized."""

    chunk_id: str = Field(description="A unique identifier for the chunk (e.g., 'doc-123-chunk-0').")
    text: str = Field(description="The text content of the chunk.")
    metadata: dict[str, Any] = Field(description="Metadata associated with the chunk, like source URL.")


class KnowledgePersistenceResult(BaseModel):
    """The output confirming the successful persistence of knowledge."""

    document_url: str = Field(description="The URL of the created or updated document in Outline.")
    vector_ids: list[str] = Field(description="A list of the unique IDs for the vectors upserted into Qdrant.")
