import pytest
from unittest.mock import patch
from agents_research.url_selection import UrlSelectionAgent

def test_url_selection_agent_creation():
    agent = UrlSelectionAgent(topic="test topic")
    assert agent is not None

@patch('agents_research.url_selection.UrlSelectionAgent._call_llm')
def test_select_urls(mock_call_llm):
    # Arrange
    mock_call_llm.return_value = "1. YES\n2. NO\n3. YES"
    agent = UrlSelectionAgent(topic="test topic")
    search_results = [
        {"url": "https://example.com/relevant"},
        {"url": "https://example.com/irrelevant"},
        {"url": "https://example.com/another_relevant"}
    ]

    # Act
    relevant_urls = agent.select_urls(search_results)

    # Assert
    assert relevant_urls == [
        "https://example.com/relevant",
        "https://example.com/another_relevant"
    ]
    mock_call_llm.assert_called_once()