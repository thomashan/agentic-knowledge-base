import pytest
from agents_research.url_selection import UrlSelectionAgent

@pytest.mark.integration
def test_url_selection_agent_integration_simple(llm_factory):
    # Arrange
    llm = llm_factory("qwen2:0.5b")
    agent = UrlSelectionAgent(topic="artificial intelligence", llm=llm)
    search_results = [
        {"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"},
        {"url": "https://www.imdb.com/title/tt0212720/"},
    ]

    # Act
    relevant_urls = agent.select_urls_simple(search_results)

    # Assert
    assert isinstance(relevant_urls, list)
