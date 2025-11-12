from unittest.mock import MagicMock, patch

import pytest
from agents_intelligence.models import IntelligenceReport, KeyFinding
from agents_knowledge.knowledge import KnowledgeAgent
from integration_documentation.outline_tool import OutlineTool
from integration_vectordb.qdrant_tool import QdrantTool
from sentence_transformers import SentenceTransformer


@pytest.fixture
def embedding_model():
    """Fixture for a real embedding model."""
    # Using a small, fast model for testing
    return SentenceTransformer("all-MiniLM-L6-v2")


@patch("requests.post")
@patch("qdrant_client.QdrantClient")
def test_knowledge_agent_integration(mock_qdrant_client, mock_requests_post, embedding_model):
    """
    Tests the full data flow of the KnowledgeAgent with real tools and a real embedding model,
    but with network calls mocked.
    """

    # --- Arrange ---
    # Mock external services
    def requests_post_side_effect(url, headers, json):
        mock_response = MagicMock()
        mock_response.status_code = 200
        if "documents.search" in url:
            # Return an empty list for search to force a create operation
            mock_response.json.return_value = {"data": []}
        elif "documents.create" in url:
            mock_response.json.return_value = {"data": {"url": "/doc/real-doc-slug"}}
        return mock_response

    mock_requests_post.side_effect = requests_post_side_effect

    mock_qdrant_instance = mock_qdrant_client.return_value
    mock_qdrant_instance.upsert.return_value = None  # The client's upsert doesn't return anything

    # Instantiate real tools
    outline_tool = OutlineTool(api_key="fake_key", base_url="http://outline.test")
    qdrant_tool = QdrantTool(host="localhost", port=6333)

    # Instantiate the agent with real dependencies
    agent = KnowledgeAgent(documentation_tool=outline_tool, vectordb_tool=qdrant_tool, embedding_model=embedding_model)

    report = IntelligenceReport(topic="Real Test Topic", executive_summary="An executive summary.", key_findings=[KeyFinding(finding_id=1, title="TF1", summary="TS1", citations=[])])

    # --- Act ---
    result = agent.persist_report(report)

    # --- Assert ---
    # Assert Outline call
    mock_requests_post.assert_any_call("http://outline.test/api/documents.search", headers=outline_tool._headers, json={"query": "Real Test Topic"})
    # This assertion depends on search returning nothing, leading to a create call.
    # A more robust test could handle both create and update.
    mock_requests_post.assert_any_call("http://outline.test/api/documents.create", headers=outline_tool._headers, json={"title": "Real Test Topic", "text": agent._format_report_to_markdown(report)})
    assert result.document_url == "http://outline.test/doc/real-doc-slug"

    # Assert Qdrant call
    mock_qdrant_instance.upsert.assert_called_once()
    upsert_args = mock_qdrant_instance.upsert.call_args[1]
    assert upsert_args["collection_name"] == "knowledge_base"
    assert len(upsert_args["points"]) > 0

    # Check the vector embedding
    first_point = upsert_args["points"][0]
    assert isinstance(first_point.vector, list)
    assert len(first_point.vector) == 384  # all-MiniLM-L6-v2 has 384 dimensions
    assert result.vector_ids[0] == first_point.id
