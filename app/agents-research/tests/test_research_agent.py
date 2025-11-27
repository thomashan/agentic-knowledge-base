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


def test_run_research_llm_driven_loop(mock_llm, mock_search_tool, mock_scrape_tool):
    # 1. Configure the mock LLM to return a sequence of actions
    mock_llm.call.side_effect = [
        """
        {
            "tool_name": "search_tool",
            "arguments": {
                "query": "test topic"
            }
        }
        """,
        """
        {
            "tool_name": "scrape_tool",
            "arguments": {
                "url": "https://example.com/1"
            }
        }
        """,
        """
        {
            "tool_name": "finish",
            "arguments": {
                "summary": "This is a summary."
            }
        }
        """,
    ]
    # 2. Instantiate the agent
    agent = ResearchAgent(llm=mock_llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool)

    # 3. Run the research
    topic = "test topic"
    research_output = agent.run_research(topic)

    # 4. Assert that the tools were called correctly
    mock_search_tool.execute.assert_called_once_with(query="test topic")
    mock_scrape_tool.execute.assert_called_once_with(url="https://example.com/1")

    # 5. Assert that the final output is correct
    assert isinstance(research_output, ResearchOutput)
    assert research_output.topic == topic
    assert research_output.summary == "This is a summary."
    assert len(research_output.results) == 1
    assert research_output.results[0].url == "https://example.com/1"
    assert research_output.results[0].content == "Scraped content"


def test_run_research_scraping_same_url_multiple_times(mock_llm, mock_search_tool, mock_scrape_tool):
    mock_llm.call.side_effect = [
        """
        {
            "tool_name": "search_tool",
            "arguments": {
                "query": "test topic"
            }
        }
        """,
        """
        {
            "tool_name": "scrape_tool",
            "arguments": {
                "url": "https://example.com/1"
            }
        }
        """,
        """
        {
            "tool_name": "scrape_tool",
            "arguments": {
                "url": "https://example.com/1"
            }
        }
        """,
        """
        {
            "tool_name": "finish",
            "arguments": {
                "summary": "This is a summary."
            }
        }
        """,
    ]
    agent = ResearchAgent(llm=mock_llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool)

    # 3. Run the research
    agent.run_research("test topic")

    mock_scrape_tool.execute.assert_called_once_with(url="https://example.com/1")


if __name__ == "__main__":
    pytest.main()
