from typing import Any

import pytest
import structlog
from agents_core.core import AbstractAgent, AbstractLLM, AbstractTask, AbstractTool
from crewai_adapter.adapter import CrewAILLM, CrewAIOrchestrator

log = structlog.get_logger()


@pytest.fixture(scope="module")
def llm(llm_factory) -> AbstractLLM:
    crew_llm = llm_factory("gemma2:2b", timeout_s=300)  # Increased timeout
    return CrewAILLM(crew_llm)


# Define a simple tool for testing
class SimpleTool(AbstractTool):
    @property
    def name(self) -> str:
        return "SimpleTool"

    @property
    def description(self) -> str:
        return "A simple tool that takes no arguments and returns a fixed string."

    def execute(self, **kwargs: Any) -> Any:
        return "Tool executed successfully!"


# Concrete implementation of AbstractAgent for testing tool use
class ToolAgent(AbstractAgent):
    def __init__(self, llm: AbstractLLM, max_retries: int = 3):
        self._llm = llm
        self._max_retries = max_retries

    @property
    def llm(self) -> AbstractLLM:
        return self._llm

    @property
    def role(self) -> str:
        return "Tool-using Agent"

    @property
    def goal(self) -> str:
        return "To use a simple tool to complete a task."

    @property
    def backstory(self) -> str:
        return "I am an agent designed to test tool usage."

    @property
    def prompt_template(self) -> None:
        return None

    @property
    def tools(self) -> list[AbstractTool]:
        return [SimpleTool()]

    @property
    def llm_config(self) -> None:
        return None

    @property
    def max_retries(self) -> int:
        return self._max_retries


# Concrete implementation of AbstractTask for testing tool use
class ToolTask(AbstractTask):
    def __init__(self, agent: AbstractAgent):
        self._agent = agent

    @property
    def description(self) -> str:
        return "Use the SimpleTool. Do not provide any arguments."

    @property
    def expected_output(self) -> str:
        return "The result from the SimpleTool, which should be 'Tool executed successfully!'"

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list["AbstractTask"] | None:
        return None


@pytest.mark.integration
def test_llm_tool_use(llm):
    """
    Tests an end-to-end agent flow involving tool usage.
    """
    orchestrator = CrewAIOrchestrator()

    agent = ToolAgent(llm=llm, max_retries=10)
    task = ToolTask(agent=agent)

    orchestrator.add_agent(agent)
    orchestrator.add_task(task)

    try:
        result = orchestrator.execute()
        log.info(f"Tool use execution result: {result.raw_output}")

        assert result is not None
        assert isinstance(result.raw_output, str)
        # Check if the final answer includes the tool's output
        results_raw = result.raw_output.lower()
        assert "successfully" in results_raw and "executed" in results_raw

    except Exception as e:
        pytest.fail(f"Tool use test failed with an unexpected error: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
