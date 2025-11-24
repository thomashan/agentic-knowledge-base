from unittest.mock import MagicMock

import pytest
from agents_core.core import AbstractLLM  # Import AbstractLLM for type hinting
from agents_research.models import SearchResult
from agents_research.url_selection import UrlSelectionAgent


@pytest.fixture
def mock_llm():
    """Fixture for a mock LLM implementing AbstractLLM."""
    mock = MagicMock(spec=AbstractLLM)
    # Default return for call, can be overridden by side_effect in tests
    mock.call.return_value = '{"default": "json"}'
    return mock


def test_url_selection_agent_creation(mock_llm):  # Inject mock_llm
    agent = UrlSelectionAgent(topic="test topic", llm=mock_llm)  # Pass mock_llm
    assert agent is not None
    assert agent.llm == mock_llm  # Verify LLM is set


def test_select_urls_with_scoring(mock_llm):  # Use mock_llm fixture
    # Arrange
    mock_llm.call.return_value = """
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
    agent = UrlSelectionAgent(topic="test topic", llm=mock_llm, relevance_threshold=6)  # Pass mock_llm
    search_results = [
        SearchResult(url="https://example.com/relevant", title="Relevant Page", summarised_content="This is a relevant page."),
        SearchResult(url="https://example.com/irrelevant", title="Irrelevant Page", summarised_content="This is an irrelevant page."),
        SearchResult(url="https://example.com/another_relevant", title="Another Relevant Page", summarised_content="This is another relevant page."),
    ]

    # Act
    relevant_urls = agent.select_urls(search_results)

    # Assert
    assert relevant_urls == ["https://example.com/relevant", "https://example.com/another_relevant"]
    mock_llm.call.assert_called_once()  # Assert on mock_llm.call


def test_select_urls_retries_on_bad_json(mock_llm):  # Use mock_llm fixture
    """
    Tests that the UrlSelectionAgent retries the LLM call if it returns malformed JSON
    when selecting URLs.
    """
    # Arrange
    bad_json_response = "This is not valid JSON."
    good_json_response = """
    [
      {
        "url": "https://example.com/relevant",
        "relevance": "9",
        "rationale": "Mock rationale for relevant page."
      }
    ]
    """
    mock_llm.call.side_effect = [bad_json_response, good_json_response]  # Mock llm.call directly

    agent = UrlSelectionAgent(topic="test topic", llm=mock_llm, relevance_threshold=6, max_retries=3)  # Pass mock_llm
    search_results = [
        SearchResult(url="https://example.com/relevant", title="Relevant Page", summarised_content="This is a relevant page."),
    ]

    # Act
    relevant_urls = agent.select_urls(search_results)

    # Assert
    assert mock_llm.call.call_count == 2
    assert relevant_urls == ["https://example.com/relevant"]


if __name__ == "__main__":
    pytest.main()
