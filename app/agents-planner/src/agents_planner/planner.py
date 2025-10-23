import json
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
        except Exception:
            return self._get_plan(goal, prompt)

    def _create_prompt(self, goal: str) -> str:
        # This prompt engineering is crucial. It instructs the LLM on its role,
        # the desired output format, and the available agent roles.
        return f"""
As an expert project planner, create a step-by-step plan to achieve the following goal: '{goal}'

The available specialist agents are:
- 'Research Agent': Gathers information from the web.
- 'Intelligence Agent': Analyzes information and synthesizes insights.
- 'Knowledge Agent': Manages and stores information in the knowledge base.

Your response MUST be a JSON object that strictly follows this Pydantic model:

class Task(BaseModel):
    task_id: int
    description: str
    expected_output: str
    agent: str
    context: list[int] = []
    tools: list[str] = []

class Plan(BaseModel):
    goal: str
    tasks: list[Task]

The plan should be a logical sequence of tasks. The 'context' field for a task should list the 'task_id's of any tasks that must be completed before it.

Example:
{{
    "goal": "Example Goal",
    "tasks": [
        {{
            "task_id": 1,
            "description": "First step of the plan.",
            "expected_output": "A document summarizing the first step.",
            "agent": "Research Agent",
            "context": [],
            "tools": ["search_tool"]
        }},
        {{
            "task_id": 2,
            "description": "Second step, which depends on the first.",
            "expected_output": "A report based on the summary from task 1.",
            "agent": "Intelligence Agent",
            "context": [1],
            "tools": []
        }}
    ]
}}

Now, generate the plan for the goal provided above.
"""

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
