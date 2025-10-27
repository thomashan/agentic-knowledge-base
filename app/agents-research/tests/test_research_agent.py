from unittest.mock import Mock, PropertyMock

import pytest
from agents_research.models import ResearchOutput
from agents_research.research import ResearchAgent


@pytest.fixture
def mock_llm():
    llm = Mock()
    type(llm).model = PropertyMock(return_value="some_model")
    type(llm).base_url = PropertyMock(return_value="https://some_url")
    return llm


@pytest.fixture
def mock_search_tool():
    search_tool = Mock()
    # Mock search tool to return two URLs
    search_tool.execute.return_value = [
        {"url": "https://example.com/1", "title": "Title 1", "summarised_content": "Snippet 1"},
        {"url": "https://example.com/2", "title": "Title 2", "summarised_content": "Snippet 2"},
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
    assert agent.role == "Senior Research Analyst"
    assert agent.goal == "To conduct thorough, unbiased, and data-driven research on any given topic."
    assert agent.backstory == (
        "You are a master of digital investigation, known for your ability to quickly find the most relevant and trustworthy information on the web.\n"
        "You are skilled at sifting through noise to find the signal, and you use a combination of advanced search techniques "
        "and intelligent content analysis to build a comprehensive overview of any subject."
    )
    assert agent._prompt_template is not None


def test_llm_driven_url_selection(mock_llm, mock_search_tool, mock_scrape_tool):
    agent = ResearchAgent(llm=mock_llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool)

    # Mock the UrlSelectionAgent
    agent.url_selection_agent = Mock()
    agent.url_selection_agent.select_urls.return_value = ["https://example.com/1"]

    topic = "test topic"
    research_output = agent.run_research(topic)

    # Assert that the search tool was called once
    mock_search_tool.execute.assert_called_once_with(query=topic)

    # Assert that the url_selection_agent was called once
    agent.url_selection_agent.select_urls.assert_called_once()

    # Assert that the scrape tool was only called for the URL selected by the LLM
    mock_scrape_tool.execute.assert_called_once_with(url="https://example.com/1")

    # Assert that the final output contains the correct data
    assert isinstance(research_output, ResearchOutput)
    assert research_output.topic == topic
    assert len(research_output.results) == 1
    assert research_output.results[0].url == "https://example.com/1"
    assert research_output.results[0].content == "Scraped content"
