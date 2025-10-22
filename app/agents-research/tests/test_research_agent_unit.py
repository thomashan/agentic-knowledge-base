from unittest.mock import Mock, patch

import pytest
from agents_research.models import ResearchOutput
from agents_research.research import ResearchAgent


@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.model = "test_model"
    llm.base_url = "http://localhost:1234"
    return llm


@pytest.fixture
def mock_search_tool():
    search_tool = Mock()
    # Mock search tool to return two URLs
    search_tool.execute.return_value = [
        {"url": "http://example.com/1", "title": "Title 1", "snippet": "Snippet 1"},
        {"url": "http://example.com/2", "title": "Title 2", "snippet": "Snippet 2"},
    ]
    return search_tool


@pytest.fixture
def mock_scrape_tool():
    scrape_tool = Mock()
    scrape_tool.execute.return_value = "Scraped content"
    return scrape_tool


def test_research_agent_instantiation(mock_llm, mock_search_tool, mock_scrape_tool):
    agent = ResearchAgent(llm=mock_llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool)
    assert agent is not None


@patch('agents_research.research.UrlSelectionAgent')
def test_llm_driven_url_selection(MockUrlSelectionAgent, mock_llm, mock_search_tool, mock_scrape_tool):
    # Arrange
    mock_url_selection_agent_instance = MockUrlSelectionAgent.return_value
    mock_url_selection_agent_instance.select_urls_simple.return_value = ["http://example.com/1"]

    agent = ResearchAgent(llm=mock_llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool)
    topic = "test topic"

    # Act
    research_output = agent.run_research(topic)

    # Assert that the search tool was called once
    mock_search_tool.execute.assert_called_once_with(query=topic)

    # Assert that UrlSelectionAgent was used
    MockUrlSelectionAgent.assert_called_once_with(topic=topic, llm=mock_llm)
    mock_url_selection_agent_instance.select_urls_simple.assert_called_once_with(
        [
            {"url": "http://example.com/1", "title": "Title 1", "snippet": "Snippet 1"},
            {"url": "http://example.com/2", "title": "Title 2", "snippet": "Snippet 2"},
        ]
    )

    # Assert that the scrape tool was only called for the URL selected by the LLM
    mock_scrape_tool.execute.assert_called_once_with(url="http://example.com/1")

    # Assert that the final output contains the correct data
    assert isinstance(research_output, ResearchOutput)
    assert research_output.topic == topic
    assert len(research_output.results) == 1
    assert research_output.results[0].url == "http://example.com/1"
    assert research_output.results[0].content == "Scraped content"