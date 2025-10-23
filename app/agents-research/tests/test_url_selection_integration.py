import pytest
from agents_research.models import SearchResult
from agents_research.url_selection import UrlSelectionAgent


@pytest.mark.integration
def test_url_selection_agent_integration(llm_factory):
    # Arrange
    llm = llm_factory("gemma2:2b")
    agent = UrlSelectionAgent(topic="artificial intelligence", llm=llm, relevance_threshold=6)
    search_results = [
        SearchResult(
            url="https://en.wikipedia.org/wiki/Artificial_intelligence",
            title="Artificial intelligence - Wikipedia",
            summarised_content=(
                "Artificial intelligence (AI) is intelligence—perceiving, synthesizing, and inferring "
                "information—demonstrated by machines, as opposed to intelligence displayed by animals "
                "or humans. AI research has been defined as the field of study that studies intelligent "
                "agents: any device that perceives its environment and takes actions that maximize its "
                "chance of successfully achieving its goals."
            ),
        ),
        SearchResult(
            url="https://www.imdb.com/title/tt0212720/",
            title="A.I. Artificial Intelligence (2001) - IMDb",
            summarised_content=(
                "A highly advanced robotic boy longs to become 'real' so that he can regain the love "
                "of his human mother. Directed by Steven Spielberg, starring Haley Joel Osment, Jude "
                "Law, and Frances O'Connor."
            ),
        ),
    ]

    # Act
    relevant_urls = agent.select_urls(search_results)

    # Assert
    assert isinstance(relevant_urls, list)
    assert len(relevant_urls) == 1
    assert "https://en.wikipedia.org/wiki/Artificial_intelligence" in relevant_urls
