import pytest
from pydantic import ValidationError
from agents_intelligence.models import KeyFinding, IntelligenceReport
from agents_research.models import ResearchOutput, ResearchResult

def test_create_key_finding():
    finding = KeyFinding(
        finding_id=1,
        title="Test Finding",
        summary="This is a test finding.",
        citations=["http://example.com"]
    )
    assert finding.finding_id == 1
    assert finding.title == "Test Finding"
    assert finding.summary == "This is a test finding."
    assert finding.citations == ["http://example.com"]

def test_create_intelligence_report():
    finding = KeyFinding(finding_id=1, title="Test", summary="Test")
    report = IntelligenceReport(
        topic="Test Topic",
        executive_summary="This is a test summary.",
        key_findings=[finding]
    )
    assert report.topic == "Test Topic"
    assert report.executive_summary == "This is a test summary."
    assert len(report.key_findings) == 1
    assert report.key_findings[0] == finding

def test_key_finding_validation_error():
    with pytest.raises(ValidationError):
        KeyFinding(title="Invalid Finding") # Missing required fields
