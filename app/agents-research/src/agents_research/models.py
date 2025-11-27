from typing import Any

from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    """A single piece of scraped content from a URL."""

    url: str = Field(description="The source URL of the content.")
    content: str = Field(description="The scraped textual content from the URL.")


class ResearchOutput(BaseModel):
    """The consolidated output of a research task, containing multiple results."""

    topic: str = Field(description="The original research topic.")
    summary: str = Field(description="A summary of the research findings.")
    results: list[ResearchResult] = Field(description="A list of research results from the most relevant sources.")
    history: list[dict[str, Any]] = Field(description="History of the actions took")


class SearchResult(BaseModel):
    """Represents a single search result with URL, title, and summarised content."""

    url: str = Field(description="The URL of the search result.")
    title: str = Field(description="The title of the webpage.")
    summarised_content: str | None = Field(description="A summarised version of the webpage's content.")


class UrlRelevanceScore(BaseModel):
    """Represents the relevance of a URL to a research topic."""

    url: str = Field(description="The URL of the search result.")
    relevance: float = Field(description="The relevance score of the URL to the research topic.")
    rationale: str = Field(description="A rationale for the relevance score.")
