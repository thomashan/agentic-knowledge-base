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
    Tests that the Runner correctly uses the AbstractOrchestrator
    to configure and execute a workflow.
    """
    # Arrange
    # Mock agents and tasks. The Runner shouldn't care about their implementation.
    mock_planner_agent = Mock(spec=AbstractAgent)
    mock_research_agent = Mock(spec=AbstractAgent)
    mock_plan_task = Mock(spec=AbstractTask)
    mock_research_task = Mock(spec=AbstractTask)

    agents = [mock_planner_agent, mock_research_agent]
    tasks = [mock_plan_task, mock_research_task]

    # The Runner will receive the orchestrator CLASS, not an instance
    orchestrator_cls = MockOrchestrator

    # Import the class to be tested
    from runner.runner import Runner

    # Act
    # Instantiate the Runner with the components
    runner = Runner(
        orchestrator_cls=orchestrator_cls,
        agents=agents,
        tasks=tasks,
    )
    result = runner.run("What is the future of AI?")

    # Assert
    assert result == "Mocked final answer"
    # We can't easily inspect the mock orchestrator instance created inside the runner,
    # but this test proves that the runner can take an orchestrator class,
    # run it, and return the expected result.
    # A more complex setup with spies or a factory pattern could inspect the instance,
    # but for now, this confirms the decoupling.


if __name__ == "__main__":
    pytest.main([__file__])
