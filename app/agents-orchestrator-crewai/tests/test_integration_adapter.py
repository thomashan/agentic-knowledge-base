from typing import Any
from unittest.mock import patch

from agents_core.core import AbstractAgent, AbstractTask, AbstractTool, ExecutionResult
from crewai_adapter.adapter import CrewAIOrchestrator


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
        return None


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


def test_crewai_orchestrator_integration_execution():
    """Tests the integration of CrewAIOrchestrator with mocked CrewAI execution."""
    orchestrator = CrewAIOrchestrator()
    mock_agent = MockAgent()
    orchestrator.add_agent(mock_agent)
    mock_task = MockTask(mock_agent)
    orchestrator.add_task(mock_task)

    with patch("crewai.Crew.kickoff") as mock_kickoff:
        mock_kickoff.return_value = "Simulated CrewAI Output"
        result = orchestrator.execute()

    mock_kickoff.assert_called_once()
    assert isinstance(result, ExecutionResult)
    assert result.raw_output == "Simulated CrewAI Output"
    assert result.structured_output is None
    assert result.task_outputs == []
    assert result.metadata == {}


def test_crewai_orchestrator_integration_config_passing():
    """Tests that configuration is passed correctly to CrewAI Crew."""
    config = {"process": "sequential", "verbose": True}
    orchestrator = CrewAIOrchestrator(config=config)
    mock_agent = MockAgent()
    orchestrator.add_agent(mock_agent)
    mock_task = MockTask(mock_agent)
    orchestrator.add_task(mock_task)

    with patch("crewai.Crew.__init__", return_value=None) as mock_crew_init, patch("crewai.Crew.kickoff", return_value=""):  # Mock kickoff to avoid actual execution
        orchestrator.execute()

    mock_crew_init.assert_called_once_with(
        agents=orchestrator.crewai_agents,
        tasks=orchestrator.crewai_tasks,
        process="sequential",
        verbose=True,
    )
