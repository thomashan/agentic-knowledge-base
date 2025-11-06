import json
from typing import Any

from agents_core.agent_reader import AgentDefinitionReader, AgentSchema
from agents_core.core import AbstractAgent
from agents_core.json_utils import to_json_object
from agents_research.models import ResearchOutput, ResearchResult
from pydantic import ValidationError

from .models import IntelligenceReport


class IntelligenceAgent(AbstractAgent):
    """
    The IntelligenceAgent uses an LLM to synthesize raw research data
    into a structured, insightful report.
    """

    def __init__(self, llm: Any, agent_file: str = "agent-prompts/agents-intelligence.md"):
        self._llm = llm
        reader = AgentDefinitionReader(AgentSchema)
        self.agent_definition = reader.read_agent(agent_file)

    @property
    def llm(self) -> Any:
        return self._llm

    def generate_report(self, research_output: ResearchOutput) -> IntelligenceReport:
        # Consolidate research content
        research_content = self._research_content(research_output.results)

        # Construct the prompt
        prompt = self.prompt_template.format(topic=research_output.topic, research_content=research_content)

        # Call the LLM
        response_text = self.call_llm(prompt)

        # Parse the response
        try:
            report_data: dict[str, Any] = to_json_object(response_text)
            report_data["topic"] = research_output.topic
            return IntelligenceReport(**report_data)
        except (json.JSONDecodeError, ValidationError, IndexError) as e:
            raise ValueError(f"Failed to parse LLM response into a valid intelligence report. Error: {e}") from e

    @staticmethod
    def _research_content(research_results: list[ResearchResult]) -> str:
        contents = [f"Source URL: {result.url}\nContent: {result.content}" for result in research_results]
        return "\n\n".join(contents)

    @property
    def role(self) -> str:
        return self.agent_definition.role

    @property
    def goal(self) -> str:
        return self.agent_definition.goal

    @property
    def backstory(self) -> str:
        return self.agent_definition.backstory

    @property
    def prompt_template(self) -> str:
        return self.agent_definition.prompt_template

    @property
    def tools(self) -> list[Any] | None:
        return None

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None
