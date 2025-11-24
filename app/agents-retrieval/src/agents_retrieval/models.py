from typing import Any

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """Represents a single chunk of retrieved information."""

    document_url: str = Field(description="The source URL of the document the chunk belongs to.")
    text: str = Field(description="The text content of the chunk.")
    score: float = Field(description="The similarity score of the chunk to the query.")
    metadata: dict[str, Any] = Field(description="Other metadata associated with the chunk.")


class RetrievalResult(BaseModel):
    """The output of a retrieval operation, containing relevant chunks."""

    query: str = Field(description="The original query string.")
    retrieved_chunks: list[RetrievedChunk] = Field(description="A list of the most relevant chunks found.")
