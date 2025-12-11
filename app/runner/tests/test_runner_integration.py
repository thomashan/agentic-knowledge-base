from unittest.mock import MagicMock, patch

import pytest
from agents_core.core import ExecutionResult
from agents_planner.models import Plan
from agents_planner.models import Task as PlannerTask
from runner.config import Settings

# Import the classes to be tested/mocked
from runner.runner import Runner


@patch("runner.runner.OrchestratorFactory")
@patch("runner.runner.PlannerAgent")
@patch("runner.runner.create_llm")  # Patch dependencies created within Runner
@patch("runner.runner.SentenceTransformer")
@patch("runner.runner.OutlineTool")
@patch("runner.runner.QdrantTool")
@patch("runner.runner.ResearchAgent")
@patch("runner.runner.KnowledgeAgent")
@patch("runner.runner.IntelligenceAgent")
@pytest.mark.integration
def test_runner_plan_and_execute_workflow(mock_intel_agent, mock_know_agent, mock_res_agent, mock_qdrant, mock_outline, mock_sent_trans, mock_create_llm, mock_planner_agent_class, mock_orch_factory):
    """
    Tests that the Runner correctly uses the Planner and Orchestrator
    to execute a workflow based on a query.
    """
    # Arrange
    # 1. Mock Settings
    mock_settings = MagicMock(spec=Settings)
    # Configure the mock with all attributes the Runner will access
    mock_settings.llm_model = "test_model"
    mock_settings.llm_provider = "test_provider"
    mock_settings.llm_base_url = "http://test.url"
    mock_settings.orchestrator_type = "test_orchestrator"
    mock_settings.outline_api_key = "test_key"
    mock_settings.outline_base_url = "http://test.outline"
    mock_settings.outline_collection_id = "test_collection"
    mock_settings.qdrant_host = "test_host"
    mock_settings.qdrant_grpc_port = 1234
    mock_settings.qdrant_http_port = 5678
    # Configure the mock with all attributes the Runner will access
    mock_settings.llm_model = "test_model"
    mock_settings.llm_provider = "test_provider"
    mock_settings.llm_base_url = "http://test.url"
    mock_settings.orchestrator_type = "test_orchestrator"
    mock_settings.outline_api_key = "test_key"
    mock_settings.outline_base_url = "http://test.outline"
    mock_settings.outline_collection_id = "test_collection"
    mock_settings.qdrant_host = "test_host"
    mock_settings.qdrant_grpc_port = 1234
    mock_settings.qdrant_http_port = 5678

    # 2. Mock PlannerAgent instance and its output
    mock_planner_instance = MagicMock()
    # Define a simple plan that the mock planner will return
    plan = Plan(
        goal="Test Goal",
        tasks=[
            PlannerTask(task_id=1, description="First task", agent="Planner", expected_output="Result of first task"),
            PlannerTask(task_id=2, description="Second task", agent="ResearchAgent", expected_output="Result of second task", dependencies=[1]),
        ],
    )
    mock_planner_instance.generate_plan.return_value = plan
    mock_planner_agent_class.return_value = mock_planner_instance

    # 3. Mock Orchestrator and its output
    mock_orchestrator_instance = MagicMock()
    mock_orchestrator_instance.execute.return_value = ExecutionResult(raw_output="Mocked final answer")
    mock_orch_factory.return_value.create.return_value = mock_orchestrator_instance

    # 4. Mock other agents to be added to the orchestrator
    # This is needed because the runner iterates through them. We can use a single mock.
    mock_agent_instance = MagicMock()
    mock_agent_instance.role = "ResearchAgent"  # Give it a role to match the plan
    mock_res_agent.return_value = mock_agent_instance

    # The planner agent's role is also needed for the agent_instances map
    mock_planner_instance.role = "Planner"

    # Act
    runner = Runner(settings=mock_settings)
    result = runner.run("What is the future of AI?")

    # Assert
    # Verify that the planner was asked to generate a plan with the query
    mock_planner_instance.generate_plan.assert_called_once_with("What is the future of AI?")

    # Verify that the two tasks from the plan were added to the orchestrator
    assert mock_orchestrator_instance.add_task.call_count == 2

    # Verify that the orchestrator was executed
    mock_orchestrator_instance.execute.assert_called_once()

    # Verify that the final result from the orchestrator is returned
    assert result == "Mocked final answer"


if __name__ == "__main__":
    pytest.main([__file__])
