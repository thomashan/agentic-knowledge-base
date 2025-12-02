from unittest.mock import MagicMock, patch

import pytest
from agents_intelligence.models import IntelligenceReport, KeyFinding
from agents_knowledge.knowledge import KnowledgeAgent
from documentation.outline_tool import OutlineTool
from sentence_transformers import SentenceTransformer
from vectordb.qdrant_tool import QdrantTool


@pytest.fixture
def embedding_model():
    """Fixture for a real embedding model."""
    return SentenceTransformer("all-MiniLM-L6-v2")


@patch("requests.post")
@patch("vectordb.qdrant_tool.QdrantClient")
@pytest.mark.integration
def test_knowledge_agent_integration(mock_qdrant_client, mock_requests_post, embedding_model):
    """
    Tests the full data flow of the KnowledgeAgent with real tools and a real embedding model,
    but with network calls mocked.
    """

    # --- Arrange ---
    def requests_post_side_effect(url, *args, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        if "documents.search" in url:
            mock_response.json.return_value = {"data": []}
        elif "documents.create" in url:
            mock_response.json.return_value = {"data": {"url": "/doc/real-doc-slug"}}
        return mock_response

    mock_requests_post.side_effect = requests_post_side_effect

    mock_qdrant_instance = mock_qdrant_client.return_value
    mock_qdrant_instance.upsert.return_value = None

    outline_tool = OutlineTool(api_key="fake_key", base_url="http://outline.test", collection_id="test_collection_id")
    qdrant_tool = QdrantTool(host="localhost", grpc_port=6334, http_port=6333)

    agent = KnowledgeAgent(documentation_tool=outline_tool, vectordb_tool=qdrant_tool, embedding_model=embedding_model)

    report = IntelligenceReport(topic="Real Test Topic", executive_summary="An executive summary.", key_findings=[KeyFinding(finding_id=1, title="TF1", summary="TS1", citations=[])])

    # --- Act ---
    result = agent.persist_report(report)

    # --- Assert ---
    assert result.document_url == "http://outline.test/doc/real-doc-slug"

    # Assert Qdrant call
    mock_qdrant_instance.upsert.assert_called_once()
    upsert_args = mock_qdrant_instance.upsert.call_args[1]
    assert upsert_args["collection_name"] == "knowledge_base"
    assert len(upsert_args["points"]) > 0

    first_point = upsert_args["points"][0]
    assert isinstance(first_point.vector, list)
    assert len(first_point.vector) == 384
    assert result.vector_ids[0] == first_point.id


if __name__ == "__main__":
    pytest.main([__file__])
