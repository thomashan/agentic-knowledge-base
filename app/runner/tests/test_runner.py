from unittest.mock import MagicMock, patch

import pytest
from runner.config import Settings
from runner.runner import Runner


@patch("runner.runner.OrchestratorFactory")
@patch("runner.runner.create_llm")
@patch("runner.runner.OutlineTool")
@patch("runner.runner.QdrantTool")
@patch("runner.runner.SentenceTransformer")
@patch("runner.runner.PlannerAgent")
@patch("runner.runner.ResearchAgent")
@patch("runner.runner.KnowledgeAgent")
@patch("runner.runner.IntelligenceAgent")
def test_runner_initialization_with_settings(
    mock_intel_agent, mock_know_agent, mock_res_agent, mock_plan_agent, mock_sentence_transformer, mock_qdrant_tool, mock_outline_tool, mock_create_llm, mock_orch_factory
):
    """
    Test that the Runner class initializes its tools and LLM
    using a central Settings object.
    """
    # Arrange: Create a mock Settings object with all necessary attributes
    mock_settings = MagicMock(spec=Settings)
    mock_settings.llm_model = "test-model"
    mock_settings.llm_provider = "test-provider"
    mock_settings.llm_base_url = "http://test-llm-url"
    mock_settings.orchestrator_type = "test-orchestrator"
    mock_settings.outline_api_key = "test_api_key_from_settings"
    mock_settings.outline_base_url = "http://test.outline.from.settings"
    mock_settings.outline_collection_id = "test_collection_id_from_settings"
    mock_settings.qdrant_host = "test.qdrant.from.settings"
    mock_settings.qdrant_grpc_port = 1234
    mock_settings.qdrant_http_port = 5678

    # Mock the LLM and Orchestrator creation
    mock_llm_instance = MagicMock()
    mock_llm_instance.llm.return_value = MagicMock()
    mock_create_llm.return_value = mock_llm_instance

    # Act
    # The constructor will be changed to accept a settings object
    runner = Runner(settings=mock_settings)

    # Assert: Check that create_llm was called with values from settings
    mock_create_llm.assert_called_once_with(
        model=mock_settings.llm_model,
        provider=mock_settings.llm_provider,
        base_url=mock_settings.llm_base_url,
        orchestrator_type=mock_settings.orchestrator_type,
    )

    # Assert: Check that tools were initialized with values from settings
    mock_outline_tool.assert_called_once_with(
        api_key=mock_settings.outline_api_key,
        base_url=mock_settings.outline_base_url,
        collection_id=mock_settings.outline_collection_id,
    )

    mock_qdrant_tool.assert_called_once_with(
        host=mock_settings.qdrant_host,
        grpc_port=mock_settings.qdrant_grpc_port,
        http_port=mock_settings.qdrant_http_port,
    )

    assert runner is not None


if __name__ == "__main__":
    pytest.main([__file__])
