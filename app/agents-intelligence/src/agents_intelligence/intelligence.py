import json
import re
from typing import Any

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
    def tools(self) -> list[AbstractTool] | None:
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
        content_str = "\n\n---\n\n".join([f"Source URL: {res.url}\nContent: {res.content}" for res in research_output.results])

        return (
            f"As a Lead Strategy Analyst, your task is to analyze the following raw research data and "
            f"synthesize it into a structured report.\n\n"
            f"The research was conducted on the topic: '{research_output.topic}'\n\n"
            f"**Raw Data:**\n---\n{content_str}\n---\n\n"
            f"**Your Task:**\n"
            f"1.  Write a concise **executive_summary** of the entire topic based on the provided data.\n"
            f"2.  Identify the most important **key_findings**. Each finding must have the following fields: `finding_id`, `title`, `summary`, and `citations`. The `citations` field must be a list of source URLs that support the finding.\n\n"
            f"Your response MUST be a JSON object that strictly follows this Pydantic model:\n\n"
            f"class KeyFinding(BaseModel):\n"
            f"    finding_id: int\n"
            f"    title: str\n"
            f"    summary: str\n"
            f"    citations: List[str]\n\n"
            f"class IntelligenceReport(BaseModel):\n"
            f"    topic: str\n"
            f"    executive_summary: str\n"
            f"    key_findings: List[KeyFinding]\n\n"
            f"Now, generate the structured report based on the raw data provided."
        )

    def _parse_response(self, response_text: str, topic: str) -> IntelligenceReport:
        try:
            json_match = re.search(r"```json\n({.*})\n```", response_text, re.DOTALL)
            response_json = json_match.group(1) if json_match else response_text

            report_data = json.loads(response_json)
            report_data["topic"] = topic

            # Extract URLs from citations
            for finding in report_data.get("key_findings", []):
                if "citations" in finding and isinstance(finding["citations"], list):
                    finding["citations"] = [citation.get("url") for citation in finding["citations"] if isinstance(citation, dict) and "url" in citation]

            return IntelligenceReport(**report_data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Failed to parse LLM response into a valid intelligence report. Error: {e}\nResponse:\n{response_text}") from e
