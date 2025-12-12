from typing import Any

import pytest
from agents_core.core import AbstractAgent, AbstractLLM, AbstractTask, AbstractTool
from crewai_adapter.adapter import CrewAIOrchestrator, CrewAILLM


class DummyMultiCommandTool(AbstractTool):
    @property
    def name(self) -> str:
        return "Dummy Multi-Command Tool"

    @property
    def description(self) -> str:
        return (
            "A dummy tool with multiple commands. "
            "Available commands: 'add', 'subtract'."
        )

    def execute(self, **kwargs: Any) -> Any:
        command = kwargs.pop("command", None)
        if command == "add":
            return self.add(**kwargs)
        elif command == "subtract":
            return self.subtract(**kwargs)
        else:
            raise ValueError(f"Unknown command: {command}")

    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b


class TestAgent(AbstractAgent):
    def __init__(self, role: str, goal: str, backstory: str, llm: AbstractLLM, tools: list[AbstractTool]):
        self._role = role
        self._goal = goal
        self._backstory = backstory
        self._llm = llm
        self._tools = tools

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
    def prompt_template(self) -> str | None:
        return None

    @property
    def tools(self) -> list[AbstractTool] | None:
        return self._tools

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    @property
    def llm(self) -> AbstractLLM | None:
        return self._llm

    @property
    def max_retries(self) -> int:
        return 3


class TestTask(AbstractTask):
    def __init__(self, description: str, expected_output: str, agent: AbstractAgent):
        self._description = description
        self._expected_output = expected_output
        self._agent = agent

    @property
    def description(self) -> str:
        return self._description

    @property
    def expected_output(self) -> str:
        return self._expected_output

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list["AbstractTask"]:
        return []


@pytest.mark.integration
def test_agent_with_dummy_tool(llm_factory):
    llm = CrewAILLM(llm_factory("ollama", "gemma2:2b"))

    dummy_tool = DummyMultiCommandTool()

    agent = TestAgent(
        role="Calculator",
        goal="Perform calculations.",
        backstory="A simple calculator agent.",
        llm=llm,
        tools=[dummy_tool],
    )

    task_prompt = "Use the 'add' command from the 'Dummy Multi-Command Tool' to add 5 and 3."

    task = TestTask(description=task_prompt, expected_output="The result of the addition.", agent=agent)

    orchestrator = CrewAIOrchestrator(config={"verbose": True})
    orchestrator.add_agent(agent)
    orchestrator.add_task(task)

    result = orchestrator.execute()

    assert "8" in result.raw_output
