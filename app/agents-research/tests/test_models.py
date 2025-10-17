import pytest
from agents_research.models import ResearchOutput, ResearchResult
from pydantic import ValidationError


def test_create_research_result():
    result = ResearchResult(url="http://example.com", content="Test content")
    assert result.url == "http://example.com"
    assert result.content == "Test content"


def test_create_research_output():
    result1 = ResearchResult(url="http://example.com/1", content="Content 1")
    result2 = ResearchResult(url="http://example.com/2", content="Content 2")
    output = ResearchOutput(topic="Test Topic", results=[result1, result2])
    assert output.topic == "Test Topic"
    assert len(output.results) == 2
    assert output.results[0] == result1


def test_research_result_validation_error():
    with pytest.raises(ValidationError):
        ResearchResult(url="http://example.com")  # Missing content
