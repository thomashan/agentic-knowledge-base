from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    """A single piece of scraped content from a URL."""

    url: str = Field(description="The source URL of the content.")
    content: str = Field(description="The scraped textual content from the URL.")


class ResearchOutput(BaseModel):
    """The consolidated output of a research task, containing multiple results."""

    topic: str = Field(description="The original research topic.")
    results: list[ResearchResult] = Field(description="A list of research results from the most relevant sources.")
