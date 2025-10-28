from unittest.mock import MagicMock

import pytest
from agents_intelligence.intelligence import IntelligenceAgent
from agents_intelligence.models import IntelligenceReport, KeyFinding
from agents_research.models import ResearchOutput, ResearchResult


@pytest.fixture
def mock_llm():
    """Fixture for a mock LLM."""
    llm = MagicMock()
    # Hardcoded JSON response for the mock LLM
    llm.call.return_value = """
    {
        "executive_summary": "This is a mock executive summary.",
        "key_findings": [
            {
                "finding_id": 1,
                "title": "Mock Finding 1",
                "summary": "This is the summary for mock finding 1.",
                "citations": ["http://example.com/source1"]
            }
        ]
    }
    """
    return llm


def test_generate_report_unit(mock_llm):
    """
    Tests the generate_report method of the IntelligenceAgent with a mock LLM.
    """
    # Arrange
    agent = IntelligenceAgent(llm=mock_llm)
    research_output = ResearchOutput(
        topic="Test Topic",
        summary="A brief summary of the research.",
        results=[ResearchResult(url="http://example.com/source1", content="Content from source 1."), ResearchResult(url="http://example.com/source2", content="Content from source 2.")],
    )

    # Act
    report = agent.generate_report(research_output)
    # prompt_arg = mock_llm.call

    # Assert
    assert isinstance(report, IntelligenceReport)
    assert report.topic == "Test Topic"
    assert report.executive_summary == "This is a mock executive summary."
    assert len(report.key_findings) == 1
    assert isinstance(report.key_findings[0], KeyFinding)
    assert report.key_findings[0].title == "Mock Finding 1"
    assert report.key_findings[0].citations == ["http://example.com/source1"]

    # Verify that the LLM was called with the correct prompt structure
    mock_llm.call.assert_called_once()
    prompt_arg = mock_llm.call.call_args[0][0]
    assert "Test Topic" in prompt_arg
    assert "Content from source 1" in prompt_arg
    assert "Content from source 2" in prompt_arg
