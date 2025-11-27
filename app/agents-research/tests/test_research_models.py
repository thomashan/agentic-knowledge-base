import pytest
from agents_research.models import ResearchOutput, ResearchResult
from pydantic import ValidationError


def test_create_research_result():
    result = ResearchResult(url="https://example.com", content="Test content")
    assert result.url == "https://example.com"
    assert result.content == "Test content"


def test_create_research_output():
    result1 = ResearchResult(url="https://example.com/1", content="Content 1")
    result2 = ResearchResult(url="https://example.com/2", content="Content 2")
    output = ResearchOutput(topic="Test Topic", summary="Test topic summary", results=[result1, result2], history=[])
    assert output.topic == "Test Topic"
    assert output.summary == "Test topic summary"
    assert len(output.results) == 2
    assert output.results[0] == result1


def test_research_result_validation_error():
    with pytest.raises(ValidationError):
        ResearchResult(url="https://example.com")  # Missing content


if __name__ == "__main__":
    pytest.main()
