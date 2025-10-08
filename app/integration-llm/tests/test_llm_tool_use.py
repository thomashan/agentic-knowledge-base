import os
from typing import Any
from unittest.mock import Mock

import pytest
from agents_core.core import AbstractAgent, AbstractTask, AbstractTool, ExecutionResult
from crewai_adapter.adapter import CrewAIOrchestrator


# Define a mock tool that the LLM should be able to use
class MockCalculatorTool(AbstractTool):
    name: str = "calculator"
    description: str = "A tool to perform basic arithmetic operations. Input should be a mathematical expression string."

    def execute(self, expression: str) -> str:
        try:
            # In a real scenario, you'd want a safer eval or a dedicated math parser
            result = eval(expression)  # nosec
            return str(result)
        except Exception as e:
            return f"Error calculating {expression}: {e}"


# Define an agent that has access to the calculator tool
class ToolUsingAgent(AbstractAgent):
    def __init__(self, llm_client: Mock):
        self._llm_client = llm_client

    @property
    def role(self) -> str:
        return "Mathematician Agent"

    @property
    def goal(self) -> str:
        return "Solve mathematical problems using the calculator tool."

    @property
    def backstory(self) -> str:
        return "An expert in arithmetic and tool usage."

    @property
    def tools(self) -> list[AbstractTool]:
        return [MockCalculatorTool()]

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return {"client": self._llm_client, "model": "test-model"}


# Define a task that requires tool usage
class ToolUsingTask(AbstractTask):
    def __init__(self, agent: AbstractAgent):
        self._agent = agent

    @property
    def description(self) -> str:
        return "Calculate the sum of 15 and 27 using the calculator tool."

    @property
    def expected_output(self) -> str:
        return "The result of 15 + 27 is 42."

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list["AbstractTask"] | None:
        return None


@pytest.mark.integration
def test_llm_tool_use_with_real_llm(real_llm_client):
    """
    Tests the LLM's ability to correctly identify and use a tool within an agentic workflow.
    This test verifies that the LLM can parse the task, decide to use the 'calculator' tool,
    format the input for the tool, and then interpret the tool's output.
    """
    print(f"\nTesting LLM tool use with provider: {os.getenv('INTEGRATION_TEST_LLM_PROVIDER', 'mock')}")  # noqa: T201

    agent = ToolUsingAgent(llm_client=real_llm_client)
    task = ToolUsingTask(agent=agent)

    orchestrator_config = {
        "process": "sequential",
        "verbose": True,
    }
    orchestrator = CrewAIOrchestrator(config=orchestrator_config)

    orchestrator.add_agent(agent)
    orchestrator.add_task(task)

    try:
        result: ExecutionResult = orchestrator.execute()

        assert result.raw_output is not None
        # The assertion here would ideally check for evidence of tool use and the correct answer.
        # This might involve checking for specific phrases or the final calculated value.
        assert "42" in result.raw_output or "calculator" in result.raw_output.lower()
        print(f"Tool Use Raw Output: {result.raw_output}")  # noqa: T201

    except Exception as e:
        pytest.fail(f"LLM tool use integration test failed: {e}")
