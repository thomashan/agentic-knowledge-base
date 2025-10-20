import json
from pathlib import Path
from typing import Any

from agents_core.core import AbstractAgent, AbstractTool
from agents_core.json_utils import to_json_object
from pydantic import ValidationError

from .models import Plan


class PlannerAgent(AbstractAgent):
    """
    The PlannerAgent uses an LLM to decompose a high-level goal
    into a structured plan of tasks.
    """

    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = self._load_prompt_template()

    @staticmethod
    def _load_prompt_template() -> str:
        base_path = Path(__file__).parent.parent.parent.parent.parent / "agent-prompts"
        prompt_path = base_path / "agents-planner.md"
        return prompt_path.read_text()

    @property
    def role(self) -> str:
        return "Expert Project Planner"

    @property
    def goal(self) -> str:
        return "Decompose a high-level goal into a structured, step-by-step plan of tasks. Each task must be assigned to a specialist agent."

    @property
    def backstory(self) -> str:
        return (
            "You are a world-class project planner, renowned for your ability to break down "
            "the most complex challenges into a clear, logical sequence of actionable steps. "
            "You are a master of identifying dependencies and assigning tasks to the right "
            "specialist. Your plans are the gold standard in the industry."
        )

    @property
    def prompt_template(self) -> str:
        return "prompt template"

    @property
    def tools(self) -> list[AbstractTool] | None:
        return None

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    def generate_plan(self, goal: str) -> Plan:
        prompt = self.prompt_template.format(goal=goal)
        response_text = self.llm.call(prompt)
        plan = self._parse_response(response_text, goal)
        return plan

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
