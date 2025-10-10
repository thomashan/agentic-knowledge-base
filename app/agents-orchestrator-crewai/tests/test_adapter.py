from typing import Any
from unittest.mock import patch, Mock

from agents_core.core import AbstractAgent, AbstractTask, AbstractTool, ExecutionResult
from crewai_adapter.adapter import CrewAIOrchestrator


class MockLLM:
    """A mock LLM for testing purposes."""
    def supports_stop_words(self) -> bool:
        return True

    def call(self, *args, **kwargs) -> str:
        return "Mocked LLM response from MockLLM"


class MockAgent(AbstractAgent):
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
    def tools(self) -> list[AbstractTool]:
        return []

    @property
    def llm_config(self) -> dict[str, Any] | None:
        # Return a mock LLM client that CrewAI can accept
        return {"client": MockLLM()}


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
    mock_agent = MockAgent()
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
    mock_agent = MockAgent()
    orchestrator.add_agent(mock_agent)

    mock_task = MockTask(mock_agent)
    orchestrator.add_task(mock_task)

    assert len(orchestrator.crewai_tasks) == 1
    crewai_task = orchestrator.crewai_tasks[0]
    assert crewai_task.description == "Test Task Description"
    assert crewai_task.expected_output == "Test Expected Output"
    assert crewai_task.agent == orchestrator.crewai_agents[0]


def test_crewai_orchestrator_execute():
    """Tests the execute method of the CrewAIOrchestrator."""
    orchestrator = CrewAIOrchestrator()
    mock_agent = MockAgent()
    orchestrator.add_agent(mock_agent)
    mock_task = MockTask(mock_agent)
    orchestrator.add_task(mock_task)

    with patch("crewai.Crew.kickoff") as mock_kickoff:
        mock_kickoff.return_value = "Final output"
        result = orchestrator.execute()

    assert isinstance(result, ExecutionResult)
    assert result.raw_output == "Final output"
