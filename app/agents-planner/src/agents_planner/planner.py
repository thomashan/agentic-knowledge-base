import json
from typing import Any

from agents_core.agent_reader import AgentDefinitionReader, AgentSchema
from agents_core.core import AbstractAgent, AbstractTool, LLMError
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
        llm,
        prompt_file: str = "agent-prompts/agents-planner.md",
    ):
        self.llm = llm
        agent_definition = AgentDefinitionReader(AgentSchema).read_agent(prompt_file)
        self._role = agent_definition.role
        self._goal = agent_definition.goal
        self._backstory = agent_definition.backstory
        self._prompt_template = agent_definition.prompt_template

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
        try:
            response_text = self.llm.call(prompt)
            return self._parse_response(response_text, goal)
        except Exception as e:
            raise LLMError(f"LLM call failed: {e}") from e

    def _create_prompt(self, goal: str) -> str:
        return self._prompt_template.format(goal=goal)

    def _parse_response(self, response_text: str, goal: str) -> Plan:
        try:
            plan_data = to_json_object(response_text)

            # Ensure the goal in the plan matches the requested goal
            plan_data["goal"] = goal

            return Plan(**plan_data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Handle cases where the LLM output is not valid JSON or doesn't match the Pydantic model
            # For now, we'll raise an error. In a real system, we might have a retry loop.
            raise ValueError(f"Failed to parse LLM response into a valid plan. Error: {e}\nResponse:\n{response_text}") from e
