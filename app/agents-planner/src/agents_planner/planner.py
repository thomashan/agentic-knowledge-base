import json
from typing import Any

from agents_core.agent_reader import AgentDefinitionReader, AgentSchema
from agents_core.core import AbstractAgent, AbstractLLM, AbstractTool
from agents_core.json_utils import to_json_object
from pydantic import ValidationError

from .models import Plan


class PlannerAgent(AbstractAgent):
    """
    The PlannerAgent uses an LLM to decompose a high-level goal
    into a structured plan of tasks.
    """

    def __init__(
        self,
        llm: AbstractLLM,
        prompt_file: str = "agent-prompts/agents-planner.md",
    ):
        self._llm = llm
        agent_definition = AgentDefinitionReader(AgentSchema).read_agent(prompt_file)
        self._role = agent_definition.role
        self._goal = agent_definition.goal
        self._backstory = agent_definition.backstory
        self._prompt_template = agent_definition.prompt_template

    @property
    def llm(self) -> AbstractLLM:
        return self._llm

    @property
    def role(self) -> str:
        return self._role

    @property
    def goal(self) -> str:
        return self._goal

    @property
    def backstory(self) -> str:
        return self._backstory

    @property
    def prompt_template(self) -> str:
        return self._prompt_template

    @property
    def tools(self) -> list[AbstractTool] | None:
        return None

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    def generate_plan(self, goal: str) -> Plan:
        prompt = self._create_prompt(goal)
        return self._get_plan(goal, prompt)

    def _get_plan(self, goal: str, prompt: str) -> Plan:
        response_text = self.call_llm(prompt)
        try:
            plan_data: dict[str, Any] = to_json_object(response_text)
            return self._parse_response(goal, plan_data)
        except json.JSONDecodeError:
            return self._get_plan(goal, prompt)

    def _create_prompt(self, goal: str) -> str:
        return self._prompt_template.format(goal=goal)

    @staticmethod
    def _parse_response(goal: str, plan_data: dict[str, Any]) -> Plan:
        try:
            # Ensure the goal in the plan matches the requested goal
            plan_data["goal"] = goal

            return Plan(**plan_data)
        except ValidationError as e:
            # Handle cases where the LLM output is not valid JSON or doesn't match the Pydantic model
            # For now, we'll raise an error. In a real system, we might have a retry loop.
            raise ValueError(f"Failed to parse LLM response into a valid plan. Error: {e}\nplan_data:\n{plan_data}") from e
