from unittest.mock import Mock

import pytest
from agents_core.core import AbstractAgent, AbstractOrchestrator, AbstractTask, ExecutionResult


# 1. Create a Mock Orchestrator that adheres to the abstract interface
class MockOrchestrator(AbstractOrchestrator):
    def __init__(self, config: dict = None):
        self.agents = []
        self.tasks = []
        self._execute_mock = Mock(return_value=ExecutionResult(raw_output="Mocked final answer"))

    def add_agent(self, agent: AbstractAgent) -> None:
        self.agents.append(agent)

    def add_task(self, task: AbstractTask) -> None:
        self.tasks.append(task)

    def execute(self) -> ExecutionResult:
        return self._execute_mock()


# 2. Refactor the test
def test_runner_uses_orchestrator():
    """
    Tests that the Runner correctly uses a pre-configured AbstractOrchestrator
    to execute a workflow.
    """
    # Arrange
    # Create a mock orchestrator and pre-configure it
    mock_orchestrator = MockOrchestrator()
    mock_orchestrator.add_agent(Mock(spec=AbstractAgent))
    mock_orchestrator.add_task(Mock(spec=AbstractTask))

    # Import the class to be tested
    from runner.runner import Runner

    # Act
    # Instantiate the Runner with the pre-configured orchestrator instance
    runner = Runner(orchestrator=mock_orchestrator)
    result = runner.run("What is the future of AI?")

    # Assert
    # Verify the final result comes from the orchestrator
    assert result == "Mocked final answer"

    # Verify the orchestrator's execute method was called
    mock_orchestrator._execute_mock.assert_called_once()


if __name__ == "__main__":
    pytest.main()
