from unittest.mock import patch

from agents_research.models import SearchResult
from agents_research.url_selection import UrlSelectionAgent


def test_url_selection_agent_creation():
    agent = UrlSelectionAgent(topic="test topic")
    assert agent is not None


@patch("agents_research.url_selection.UrlSelectionAgent._call_llm")
def test_select_urls_with_scoring(mock_call_llm):
    # Arrange
    mock_call_llm.return_value = """
[
  {
    "url": "https://example.com/relevant",
    "relevance": "9",
    "rationale": "Mock rationale for relevant page."
  },
  {
    "url": "https://example.com/irrelevant",
    "relevance": "2",
    "rationale": "Mock rationale for irrelevant page."
  },
  {
    "url": "https://example.com/another_relevant",
    "relevance": "8",
    "rationale": "Mock rationale for another relevant page."
  }
]
"""
    agent = UrlSelectionAgent(topic="test topic", relevance_threshold=6)
    search_results = [
        SearchResult(url="https://example.com/relevant", title="Relevant Page", summarised_content="This is a relevant page."),
        SearchResult(url="https://example.com/irrelevant", title="Irrelevant Page", summarised_content="This is an irrelevant page."),
        SearchResult(url="https://example.com/another_relevant", title="Another Relevant Page", summarised_content="This is another relevant page."),
    ]

    # Act
    relevant_urls = agent.select_urls(search_results)

    # Assert
    assert relevant_urls == ["https://example.com/relevant", "https://example.com/another_relevant"]
    mock_call_llm.assert_called_once()
