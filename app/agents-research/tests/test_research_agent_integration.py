from unittest.mock import Mock

import pytest
from agents_research.models import ResearchOutput
from agents_research.research import ResearchAgent


@pytest.fixture
def mock_search_tool():
    search_tool = Mock()
    # Mock search tool to return a realistic set of search results
    search_tool.execute.return_value = [
        {
            "url": "https://www.crewai.com/",
            "title": "CrewAI - The AI Crew Framework",
            "summarised_content": "CrewAI helps you build sophisticated multi-agent systems to solve complex problems. Get started with our documentation and examples today.",
        },
        {
            "url": "https://github.com/crewAI/crewAI",
            "title": "crewAI/crewAI: GitHub",
            "summarised_content": "The official GitHub repository for CrewAI. Find the source code, report issues, and contribute to the project. Join our community!",
        },
        {
            "url": "https://invalid-url.example.com",
            "title": "Not a real page",
            "summarised_content": "This page does not exist and is used for testing purposes. It should not be selected by the agent.",
        },
    ]
    return search_tool


@pytest.fixture
def mock_scrape_tool():
    scrape_tool = Mock()

    def scrape_side_effect(url: str):
        if "crewai.com" in url:
            return "CrewAI is a framework for orchestrating role-playing, autonomous AI agents."
        elif "github.com" in url:
            return "This is the GitHub repository for CrewAI."
        else:
            return "Failed to scrape."

    scrape_tool.execute.side_effect = scrape_side_effect
    return scrape_tool


@pytest.mark.integration
def test_research_agent_real_llm_mock_tools(llm_factory, mock_search_tool, mock_scrape_tool):
    """
    Tests the ResearchAgent with a real LLM but mock tools to ensure
    the LLM can make a decision without network dependencies.
    """
    # 1. Get a real LLM from the factory
    llm = llm_factory("gemma2:2b")

    # 2. Instantiate the ResearchAgent
    agent = ResearchAgent(llm=llm, search_tool=mock_search_tool, scrape_tool=mock_scrape_tool)

    # 3. Define a research topic
    topic = "What is CrewAI?"

    # 4. Run the research
    research_output = agent.run_research(topic)

    # 5. Validate the output
    assert isinstance(research_output, ResearchOutput)
    assert research_output.topic == topic
    assert len(research_output.results) > 0
    # The real LLM might choose to scrape 1 or 2 of the valid URLs
    assert len(research_output.results) <= 2

    # Assert that the search tool was called
    mock_search_tool.execute.assert_called_once_with(query=topic)

    # Assert that the scrape tool was called at least once
    assert mock_scrape_tool.execute.call_count > 0

    # Assert that the invalid URL was not scraped
    for call in mock_scrape_tool.execute.call_args_list:
        assert "invalid-url" not in call.kwargs["url"]
