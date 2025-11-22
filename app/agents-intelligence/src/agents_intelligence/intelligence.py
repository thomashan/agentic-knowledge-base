from typing import Any

from agents_core.agent_reader import AgentDefinitionReader, AgentSchema
from agents_core.core import AbstractAgent, AbstractLLM
from agents_core.json_utils import to_json_object
from agents_research.models import ResearchOutput, ResearchResult

from .models import IntelligenceReport


class IntelligenceAgent(AbstractAgent):
    """
    The IntelligenceAgent uses an LLM to synthesize raw research data
    into a structured, insightful report.
    """

    def __init__(self, llm: AbstractLLM, agent_file: str = "agent-prompts/agents-intelligence.md", max_retries: int = 3):
        self._llm = llm
        reader = AgentDefinitionReader(AgentSchema)
        self.agent_definition = reader.read_agent(agent_file)
        self._max_retries = max_retries

    @property
    def llm(self) -> AbstractLLM:
        return self._llm

    def generate_report(self, research_output: ResearchOutput) -> IntelligenceReport:
        # Consolidate research content
        research_content = self._research_content(research_output.results)

        # Construct the prompt
        prompt = self.prompt_template.format(topic=research_output.topic, research_content=research_content)

        response_text = self.call_llm(prompt)
        report_data = to_json_object(response_text)

        # Add topic to report_data as it's part of IntelligenceReport model
        report_data["topic"] = research_output.topic

        return IntelligenceReport(**report_data)

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

    @property
    def max_retries(self) -> int:
        return self._max_retries
