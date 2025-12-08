import pytest
from agents_research.models import SearchResult
from agents_research.url_selection import UrlSelectionAgent


@pytest.mark.integration
def test_url_selection_agent_integration(ollama_llm_factory):
    # Arrange
    llm = ollama_llm_factory("ollama", "gemma2:2b")
    agent = UrlSelectionAgent(topic="artificial intelligence", llm=llm, relevance_threshold=6, max_retries=10)
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


@pytest.mark.integration
def test_url_selection_agent_crew_ai_integration(ollama_llm_factory):
    # Arrange
    llm = ollama_llm_factory("ollama", "gemma2:2b")
    agent = UrlSelectionAgent(topic="What is CrewAI?", llm=llm, relevance_threshold=4, max_retries=10)
    search_results = [
        SearchResult(
            url="https://www.crewai.com/",
            title="CrewAI - The AI Crew Framework",
            summarised_content="CrewAI helps you build sophisticated multi-agent systems to solve complex problems. Get started with our documentation and examples today.",
        ),
        SearchResult(
            url="https://github.com/crewAI/crewAI",
            title="crewAI/crewAI: GitHub",
            summarised_content="The official GitHub repository for CrewAI. Find the source code, report issues, and contribute to the project. Join our community!",
        ),
        SearchResult(
            url="https://invalid-url.example.com",
            title="Not a real page",
            summarised_content="This page does not exist and is used for testing purposes. It should not be selected by the agent.",
        ),
    ]

    # Act
    relevant_urls = agent.select_urls(search_results)

    # Assert
    assert isinstance(relevant_urls, list)
    assert len(relevant_urls) == 2
    assert "https://www.crewai.com/" in relevant_urls
    assert "https://github.com/crewAI/crewAI" in relevant_urls


if __name__ == "__main__":
    pytest.main([__file__])
