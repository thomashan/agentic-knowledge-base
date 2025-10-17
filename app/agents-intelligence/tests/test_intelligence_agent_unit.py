import pytest
from unittest.mock import Mock
from agents_intelligence.intelligence import IntelligenceAgent
from agents_intelligence.models import IntelligenceReport
from agents_research.models import ResearchOutput, ResearchResult

@pytest.fixture
def mock_llm():
    llm = Mock()
    report_json = '''
    {
        "topic": "Test Topic",
        "executive_summary": "This is a mock executive summary.",
        "key_findings": [
            {
                "finding_id": 1,
                "title": "Mock Finding 1",
                "summary": "Summary of mock finding 1.",
                "citations": ["http://example.com/1"]
            }
        ]
    }
    '''
    llm.call.return_value = report_json
    return llm

@pytest.fixture
def sample_research_output():
    return ResearchOutput(
        topic="Test Topic",
        results=[
            ResearchResult(url="http://example.com/1", content="This is content about finding 1."),
            ResearchResult(url="http://example.com/2", content="This is other content."),
        ]
    )

def test_intelligence_agent_instantiation(mock_llm):
    agent = IntelligenceAgent(llm=mock_llm)
    assert agent is not None

def test_intelligence_agent_report_generation(mock_llm, sample_research_output):
    agent = IntelligenceAgent(llm=mock_llm)
    report = agent.generate_report(sample_research_output)

    assert isinstance(report, IntelligenceReport)
    assert report.topic == "Test Topic"
    assert report.executive_summary == "This is a mock executive summary."
    assert len(report.key_findings) == 1
    assert report.key_findings[0].title == "Mock Finding 1"
    mock_llm.call.assert_called_once()
