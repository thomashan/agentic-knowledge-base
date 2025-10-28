# We will depend on the models from the research agent
from pydantic import BaseModel, Field


class KeyFinding(BaseModel):
    """A single, structured insight synthesized from the research data."""

    finding_id: int = Field(description="A unique identifier for the finding.")
    title: str = Field(description="A concise title for the key finding.")
    summary: str = Field(description="A detailed summary of the finding, including its implications.")
    citations: list[str] = Field(default_factory=list, description="A list of source URLs that support this finding.")


class IntelligenceReport(BaseModel):
    """A structured report containing synthesized insights from raw research."""

    topic: str = Field(description="The original research topic.")
    executive_summary: str = Field(description="A high-level summary of the entire research topic.")
    key_findings: list[KeyFinding] = Field(description="A list of the most important, structured findings from the research.")
