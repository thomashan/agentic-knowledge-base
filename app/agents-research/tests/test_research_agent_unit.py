from unittest.mock import Mock, PropertyMock, patch

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


def test_research_agent_instantiation(mock_llm, mock_search_tool, mock_scrape_tool, tmp_path):
    # Create a dummy agent file for the unit test
    agent_file = tmp_path / "research_agent_unit.md"
    agent_file.write_text("""
## Role

The role of the research agent for unit tests.

## Goal

The goal of the research agent for unit tests.

## Backstory

The backstory of the research agent for unit tests.
""")
    agent = ResearchAgent(llm=mock_llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool, agent_file=str(agent_file))
    assert agent is not None


@patch("agents_research.url_selection.completion")
def test_llm_driven_url_selection(mock_completion, mock_llm, mock_search_tool, mock_scrape_tool, tmp_path):
    # Create a dummy agent file for the unit test
    agent_file = tmp_path / "research_agent_unit.md"
    agent_file.write_text("""
## Role

The role of the research agent for unit tests.

## Goal

The goal of the research agent for unit tests.

## Backstory

The backstory of the research agent for unit tests.
""")
    agent = ResearchAgent(llm=mock_llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool, agent_file=str(agent_file))
    topic = "test topic"

    mock_response = Mock()
    mock_choice = Mock()
    mock_choice.message.content = '["https://example.com/1"]'
    mock_response.choices = [mock_choice]
    mock_completion.return_value = mock_response

    research_output = agent.run_research(topic)

    # Assert that the search tool was called once
    mock_search_tool.execute.assert_called_once_with(query=topic)

    # Assert that the LLM was called once to decide which URLs to scrape
    mock_completion.assert_called_once()

    # Assert that the scrape tool was only called for the URL selected by the LLM
    mock_scrape_tool.execute.assert_called_once_with(url="https://example.com/1")

    # Assert that the final output contains the correct data
    assert isinstance(research_output, ResearchOutput)
    assert research_output.topic == topic
    assert len(research_output.results) == 1
    assert research_output.results[0].url == "https://example.com/1"
    assert research_output.results[0].content == "Scraped content"
