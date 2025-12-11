from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from agents_core.core import AbstractAgent, AbstractTask, AbstractTool, ExecutionResult
from crewai.llm import LLM
from crewai_adapter.adapter import CrewAIOrchestrator


class MockAgent(AbstractAgent):
    def __init__(self, llm: LLM | None = None):
        self._llm = llm

    @property
    def llm(self) -> LLM | None:
        return self._llm

    @property
    def role(self) -> str:
        return "Test Role"

    @property
    def goal(self) -> str:
        return "Test Goal"

    @property
    def backstory(self) -> str:
        return "Test Backstory"

    @property
    def prompt_template(self) -> None:
        return None

    @property
    def tools(self) -> list[AbstractTool]:
        return []

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    @property
    def max_retries(self) -> int:
        return 1


class MockTask(AbstractTask):
    def __init__(self, agent: AbstractAgent):
        self._agent = agent

    @property
    def description(self) -> str:
        return "Test Task Description"

    @property
    def expected_output(self) -> str:
        return "Test Expected Output"

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list["""AbstractTask"""] | None:
        return None


def test_crewai_orchestrator_instantiation():
    """Tests the instantiation of the CrewAIOrchestrator."""
    orchestrator = CrewAIOrchestrator()
    assert orchestrator is not None


def test_crewai_orchestrator_initialization():
    """Tests the initialization of the CrewAIOrchestrator."""
    orchestrator = CrewAIOrchestrator()
    assert orchestrator.crewai_agents == []
    assert orchestrator.crewai_tasks == []
    assert orchestrator.agent_map == {}


def test_crewai_orchestrator_add_agent():
    """Tests the add_agent method of the CrewAIOrchestrator."""
    orchestrator = CrewAIOrchestrator()
    mock_llm = MagicMock(spec=LLM)  # Create mock LLM
    mock_agent = MockAgent(llm=mock_llm)  # Pass the mock LLM
    orchestrator.add_agent(mock_agent)

    assert len(orchestrator.crewai_agents) == 1
    crewai_agent = orchestrator.crewai_agents[0]
    assert crewai_agent.role == "Test Role"
    assert crewai_agent.goal == "Test Goal"
    assert crewai_agent.backstory == "Test Backstory"
    assert orchestrator.agent_map[id(mock_agent)] == crewai_agent


def test_crewai_orchestrator_add_task():
    """Tests the add_task method of the CrewAIOrchestrator."""
    orchestrator = CrewAIOrchestrator()
    mock_llm = MagicMock(spec=LLM)  # Create mock LLM
    mock_agent = MockAgent(llm=mock_llm)  # Pass the mock LLM
    orchestrator.add_agent(mock_agent)

    mock_task = MockTask(mock_agent)
    orchestrator.add_task(mock_task)

    assert len(orchestrator.crewai_tasks) == 1
    crewai_task = orchestrator.crewai_tasks[0]
    assert crewai_task.description == "Test Task Description"
    assert crewai_task.expected_output == "Test Expected Output"
    assert crewai_task.agent == orchestrator.crewai_agents[0]


@patch("crewai_adapter.adapter.Crew")
def test_crewai_orchestrator_execute_initializes_crew_correctly(mock_crew):
    """Tests that the execute method initializes and runs a CrewAI Crew correctly."""
    # 1. Arrange
    orchestrator = CrewAIOrchestrator(config={"some_config": "value"})
    mock_llm = MagicMock(spec=LLM)  # Create mock LLM
    mock_agent = MockAgent(llm=mock_llm)  # Pass the mock LLM
    orchestrator.add_agent(mock_agent)
    mock_task = MockTask(mock_agent)
    orchestrator.add_task(mock_task)

    mock_crew_instance = mock_crew.return_value
    mock_crew_instance.kickoff.return_value = "Final output"

    # 2. Act
    result = orchestrator.execute()

    # 3. Assert
    # Check that Crew was instantiated correctly
    mock_crew.assert_called_once_with(
        agents=orchestrator.crewai_agents,
        tasks=orchestrator.crewai_tasks,
        some_config="value",
    )

    # Check that kickoff was called
    mock_crew_instance.kickoff.assert_called_once()

    # Check the result
    assert isinstance(result, ExecutionResult)
    assert result.raw_output == "Final output"


if __name__ == "__main__":
    pytest.main([__file__])
