import json
import re
from typing import Any, List

from agents_core.core import AbstractAgent, AbstractTool
from agents_research.models import ResearchOutput
from pydantic import ValidationError

from .models import IntelligenceReport


class IntelligenceAgent(AbstractAgent):
    """
    The IntelligenceAgent uses an LLM to synthesize raw research data
    into a structured, insightful report.
    """

    def __init__(self, llm: Any):
        self.llm = llm

    @property
    def role(self) -> str:
        return "Lead Strategy Analyst"

    @property
    def goal(self) -> str:
        return "To analyze unstructured data and synthesize it into a structured, insightful report with an executive summary and key findings."

    @property
    def backstory(self) -> str:
        return (
            "You are a brilliant strategy analyst with a talent for seeing the bigger picture. "
            "You excel at taking large volumes of raw, unstructured text and distilling them "
            "into concise, actionable intelligence. Your reports are legendary for their clarity, "
            "insight, and strategic value."
        )

    @property
    def tools(self) -> List[AbstractTool] | None:
        return None

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    def generate_report(self, research_output: ResearchOutput) -> IntelligenceReport:
        prompt = self._create_prompt(research_output)
        response_text = self.llm.call(prompt)
        report = self._parse_response(response_text, research_output.topic)
        return report

    def _create_prompt(self, research_output: ResearchOutput) -> str:
        content_str = "\n\n---\n\n".join(
            [f"Source URL: {res.url}\nContent: {res.content}" for res in research_output.results]
        )

        return f"""
As a Lead Strategy Analyst, your task is to analyze the following raw research data and synthesize it into a structured report.

The research was conducted on the topic: '{research_output.topic}'

**Raw Data:**
---
{content_str}
---

**Your Task:**
1.  Write a concise **executive_summary** of the entire topic based on the provided data.
2.  Identify the most important **key_findings**. Each finding should have a unique `finding_id`, a `title`, a `summary`, and a list of `citations` (the source URLs that support the finding).

Your response MUST be a JSON object that strictly follows this Pydantic model:

class KeyFinding(BaseModel):
    finding_id: int
    title: str
    summary: str
    citations: List[str]

class IntelligenceReport(BaseModel):
    topic: str
    executive_summary: str
    key_findings: List[KeyFinding]

Now, generate the structured report based on the raw data provided.
"""

    def _parse_response(self, response_text: str, topic: str) -> IntelligenceReport:
        try:
            json_match = re.search(r"```json\n({.*})\n```", response_text, re.DOTALL)
            if json_match:
                response_json = json_match.group(1)
            else:
                response_json = response_text

            report_data = json.loads(response_json)
            report_data['topic'] = topic

            return IntelligenceReport(**report_data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(
                f"Failed to parse LLM response into a valid intelligence report. Error: {e}\nResponse:\n{response_text}"
            ) from e
