from unittest.mock import MagicMock, patch

import pytest

# The app object from the main module to be tested
from runner.main import app
from typer.testing import CliRunner

runner = CliRunner()


@patch("runner.main.BasicTask", autospec=True)
@patch("runner.main.PlannerAgent", autospec=True)
@patch("runner.main.LlmFactory", autospec=True)
@patch("runner.main.CrewAIOrchestrator", autospec=True)
@patch("runner.main.Runner", autospec=True)
def test_main_cli_with_planner_workflow(
    mock_runner_cls: MagicMock,
    mock_orchestrator_cls: MagicMock,
    mock_llm_factory_cls: MagicMock,
    mock_planner_agent_cls: MagicMock,
    mock_basic_task_cls: MagicMock,
):
    """
    Tests that the CLI correctly assembles the 'planner' workflow and passes
    the configured orchestrator to the Runner.
    """
    # Arrange
    mock_llm_instance = MagicMock()
    mock_llm_factory_cls.create_llm.return_value = mock_llm_instance

    mock_planner_instance = mock_planner_agent_cls.return_value
    mock_task_instance = mock_basic_task_cls.return_value

    mock_orchestrator_instance = mock_orchestrator_cls.return_value

    mock_runner_instance = mock_runner_cls.return_value
    mock_runner_instance.run.return_value = "Planner says hello"

    # Act
    test_query = "What is Ollama?"
    result = runner.invoke(app, [test_query, "--workflow", "planner"])

    # Assert
    assert result.exit_code == 0
    assert "Planner says hello" in result.stdout

    # Verify LLM and Agent creation
    mock_llm_factory_cls.create_llm.assert_called_once()
    mock_planner_agent_cls.assert_called_once_with(llm=mock_llm_instance)

    # Verify Orchestrator assembly
    mock_orchestrator_cls.assert_called_once()
    mock_orchestrator_instance.add_agent.assert_called_once_with(mock_planner_instance)
    mock_orchestrator_instance.add_task.assert_called_once_with(mock_task_instance)

    # Verify Runner was instantiated with the pre-configured orchestrator
    mock_runner_cls.assert_called_once_with(orchestrator=mock_orchestrator_instance)
    mock_runner_instance.run.assert_called_once_with(test_query)


@patch("runner.main.LlmFactory", autospec=True)
def test_main_cli_with_unknown_workflow(mock_create_llm: MagicMock):
    """
    Tests that the CLI exits with an error if an unknown workflow is specified.
    """
    # Act
    test_query = "Some query"
    unknown_workflow = "non-existent-workflow"
    result = runner.invoke(app, [test_query, "--workflow", unknown_workflow])

    # Assert
    assert result.exit_code != 0
    assert f"Error: Unknown workflow: {unknown_workflow}" in result.stderr
    mock_create_llm.assert_not_called()


@patch("runner.main.BasicTask", autospec=True)
@patch("runner.main.PlannerAgent", autospec=True)
# @patch('runner.main.ResearchAgent', autospec=True) # Removed
@patch("runner.main.IntelligenceAgent", autospec=True)
@patch("runner.main.KnowledgeAgent", autospec=True)
@patch("runner.main.RetrievalAgent", autospec=True)
@patch("runner.main.OutlineTool", autospec=True)
@patch("runner.main.QdrantTool", autospec=True)
# @patch('runner.main.SearxNGSearchTool', autospec=True) # Removed
# @patch('runner.main.AgenticSeekTool', autospec=True) # Removed
@patch("runner.main.LlmFactory", autospec=True)
@patch("runner.main.CrewAIOrchestrator", autospec=True)
@patch("runner.main.Runner", autospec=True)
def test_main_cli_with_full_rag_workflow(
    mock_runner_cls: MagicMock,
    mock_orchestrator_cls: MagicMock,
    mock_llm_factory_cls: MagicMock,
    mock_planner_agent_cls: MagicMock,
    # mock_research_agent_cls: MagicMock, # Removed
    mock_intelligence_agent_cls: MagicMock,
    mock_knowledge_agent_cls: MagicMock,
    mock_retrieval_agent_cls: MagicMock,
    mock_outline_tool_cls: MagicMock,
    mock_qdrant_tool_cls: MagicMock,
    # mock_searxng_search_tool_cls: MagicMock, # Removed
    # mock_agentic_seek_tool_cls: MagicMock, # Removed
    mock_basic_task_cls: MagicMock,
):
    """
    Tests that the CLI correctly assembles the (simplified) 'full-rag' workflow,
    instantiates all remaining agents and tools, and passes the configured
    orchestrator to the Runner.
    """
    # Arrange
    # Mock return values for factories and constructors
    mock_llm_instance = MagicMock()
    mock_llm_factory_cls.create_llm.return_value = mock_llm_instance

    mock_qdrant_tool_instance = mock_qdrant_tool_cls.return_value
    mock_outline_tool_instance = mock_outline_tool_cls.return_value
    # Removed: mock_searxng_search_tool_instance = mock_searxng_search_tool_cls.return_value
    # Removed: mock_agentic_seek_tool_instance = mock_agentic_seek_tool_cls.return_value

    # Removed: mock_research_instance = mock_research_agent_cls.return_value

    # Orchestrator and Runner mocks
    mock_orchestrator_instance = mock_orchestrator_cls.return_value
    mock_runner_instance = mock_runner_cls.return_value
    mock_runner_instance.run.return_value = "Full RAG workflow completed"

    # Tasks mocks
    # Removed: mock_research_task_instance = mock_basic_task_cls.return_value

    # Act
    test_query = "Research the latest AI trends"
    result = runner.invoke(app, [test_query, "--workflow", "full-rag"])

    # Assert
    assert result.exit_code == 0
    assert "Full RAG workflow completed" in result.stdout

    # 1. Verify LLM and Tool instantiation
    mock_llm_factory_cls.create_llm.assert_called_once()
    mock_qdrant_tool_cls.assert_called_once()
    mock_outline_tool_cls.assert_called_once()
    # Removed: mock_searxng_search_tool_cls.assert_called_once()
    # Removed: mock_agentic_seek_tool_cls.assert_called_once()

    # 2. Verify Agent instantiation with correct dependencies
    mock_planner_agent_cls.assert_called_once_with(llm=mock_llm_instance)
    # Removed: mock_research_agent_cls.assert_called_once_with(...)
    mock_intelligence_agent_cls.assert_called_once_with(llm=mock_llm_instance)
    mock_knowledge_agent_cls.assert_called_once_with(llm=mock_llm_instance, qdrant_tool=mock_qdrant_tool_instance, outline_tool=mock_outline_tool_instance)
    mock_retrieval_agent_cls.assert_called_once_with(llm=mock_llm_instance, qdrant_tool=mock_qdrant_tool_instance)

    # 3. Verify Task instantiation
    assert mock_basic_task_cls.call_count == 4  # Reduced from 5
    # (Detailed assertion for each task would be too verbose, relying on call_count)

    # 4. Verify Orchestrator assembly
    mock_orchestrator_cls.assert_called_once()
    assert mock_orchestrator_instance.add_agent.call_count == 4  # Reduced from 5
    assert mock_orchestrator_instance.add_task.call_count == 4  # Reduced from 5

    # 5. Verify Runner was instantiated with the pre-configured orchestrator
    mock_runner_cls.assert_called_once_with(orchestrator=mock_orchestrator_instance)
    mock_runner_instance.run.assert_called_once_with(test_query)


if __name__ == "__main__":
    pytest.main()
