from unittest.mock import MagicMock

import numpy as np
import pytest
from agents_intelligence.models import IntelligenceReport, KeyFinding
from agents_knowledge.knowledge import KnowledgeAgent
from agents_knowledge.models import KnowledgePersistenceResult


@pytest.fixture
def mock_outline_tool():
    """Fixture for a mocked OutlineTool."""
    mock_outline_tool = MagicMock()
    mock_outline_tool.base_url = "http://example.com"
    return mock_outline_tool


@pytest.fixture
def mock_qdrant_tool():
    """Fixture for a mocked QdrantTool."""
    return MagicMock()


@pytest.fixture
def mock_embedding_model():
    """Fixture for a mocked embedding model."""
    model = MagicMock()
    # SentenceTransformer returns a numpy array
    model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    return model


@pytest.fixture
def agent(mock_outline_tool, mock_qdrant_tool, mock_embedding_model):
    """Fixture to create a KnowledgeAgent with mocked dependencies."""
    return KnowledgeAgent(documentation_tool=mock_outline_tool, vectordb_tool=mock_qdrant_tool, embedding_model=mock_embedding_model)


def test_knowledge_agent_instantiation(agent, mock_outline_tool, mock_qdrant_tool, mock_embedding_model):
    """Tests that the KnowledgeAgent can be instantiated."""
    assert agent is not None
    assert agent._documentation_tool == mock_outline_tool
    assert agent._vectordb_tool == mock_qdrant_tool
    assert agent._embedding_model == mock_embedding_model


def test_persist_report(agent, mock_outline_tool, mock_qdrant_tool):
    """
    Tests the main persist_report method of the agent.
    """
    report = IntelligenceReport(
        topic="Test Topic",
        executive_summary="This is the executive summary.",
        key_findings=[
            KeyFinding(finding_id=1, title="Finding 1", summary="Summary of finding 1.", citations=["http://a.com"]),
            KeyFinding(finding_id=2, title="Finding 2", summary="Summary of finding 2.", citations=["http://b.com"]),
        ],
    )

    mock_outline_tool.execute.return_value = {"data": {"url": "/doc/123"}}
    mock_qdrant_tool.execute.return_value = ["vec-1"]

    result = agent.persist_report(report)

    # Assert that the documentation tool was called to create/update the doc
    mock_outline_tool.execute.assert_called_once()
    call_args = mock_outline_tool.execute.call_args[1]
    assert call_args["command"] == "create_or_update_document"
    assert call_args["title"] == "Test Topic"
    assert "This is the executive summary." in call_args["content"]
    assert "Finding 1" in call_args["content"]

    # Assert that the vector db tool was called to upsert vectors
    mock_qdrant_tool.execute.assert_called_once()
    qdrant_args = mock_qdrant_tool.execute.call_args[1]
    assert qdrant_args["command"] == "upsert_vectors"
    assert qdrant_args["collection_name"] == "knowledge_base"
    assert len(qdrant_args["vectors"]) > 0

    # Assert the final result
    assert isinstance(result, KnowledgePersistenceResult)
    assert result.document_url == "http://example.com/doc/123"
    assert result.vector_ids == ["vec-1"]


if __name__ == "__main__":
    pytest.main()
