import os
from unittest.mock import MagicMock, patch

import pytest
import structlog

# Import the actual ResearchAgent
from agents_research.research import ResearchAgent
from dotenv import load_dotenv
from integration_llm.factory import create_llm

log = structlog.get_logger()


# Mock the external components to avoid ModuleNotFoundError
class MockAbstractLLM:
    """A basic mock for AbstractLLM."""

    def call(self, prompt: str) -> str:
        return "mocked LLM response"


class MockAbstractTask:
    """A basic mock for AbstractTask."""

    def __init__(self, agent, description, expected_output):
        self.agent = agent
        self.description = description
        self.expected_output = expected_output
        self.dependencies = []


# MockResearchAgent is no longer needed, using the real ResearchAgent


class MockCrewAIOrchestrator:
    """A basic mock for CrewAIOrchestrator."""

    def __init__(self, config=None):
        self.agents = []
        self.tasks = []
        self.config = config or {}

    def add_agent(self, agent):
        self.agents.append(agent)

    def add_task(self, task):
        self.tasks.append(task)

    def execute(self):
        # In this mock orchestrator, we will directly call the agent's run_research method.
        # This simulates the orchestrator driving the agent.
        if not self.agents or not self.tasks:
            raise ValueError("MockCrewAIOrchestrator requires agents and tasks to execute.")

        # Assume one agent and one task for simplicity in this integration test
        agent = self.agents[0]
        task = self.tasks[0]

        # The ResearchAgent's run_research takes topic directly
        # The topic is embedded in the task description for simplicity here
        topic = task.description.split("Research on: ")[1].strip()

        # Call the actual run_research method of the agent
        research_output = agent.run_research(topic=topic)
        return MagicMock(raw=research_output.summary)  # Mimic Crew's output structure


class MockRunner:
    """A basic mock for Runner."""

    def __init__(self, orchestrator_cls, agents, tasks, orchestrator_config=None):
        self.orchestrator = orchestrator_cls(config=orchestrator_config)
        for agent in agents:
            self.orchestrator.add_agent(agent)
        for task in tasks:
            self.orchestrator.add_task(task)

    def run(self, query: str) -> str:
        execution_result = self.orchestrator.execute()
        return execution_result.raw  # Access the raw attribute of the mock result


@pytest.fixture
def mock_search_tool():
    """Mocks the DuckDuckGoSearchTool for deterministic results."""
    mock = MagicMock()  # No spec needed as ResearchAgent is mocked too
    mock.name = "search_tool"
    mock.description = "A tool for performing web searches."
    mock.execute.return_value = [
        {"url": "https://example.com/ai-future", "title": "AI Future", "snippet": "Future of AI is bright."},
        {"url": "https://example.com/ml-trends", "title": "ML Trends", "snippet": "Latest trends in Machine Learning."},
    ]
    return mock


@pytest.fixture
def mock_scraper_tool():
    """Mocks the ScraperTool for deterministic results."""
    mock = MagicMock()  # No spec needed as ResearchAgent is mocked too
    mock.name = "scrape_tool"
    mock.description = "A tool for scraping content from web pages."
    # Use a lambda to correctly handle keyword arguments
    mock.execute.side_effect = lambda **kwargs: {
        "https://example.com/ai-future": "Content about the future of AI.",
        "https://example.com/ml-trends": "Content about machine learning trends.",
    }.get(kwargs.get("url"))
    return mock


@pytest.mark.integration
def test_openrouter_agent_workflow_integration(mock_search_tool, mock_scraper_tool):
    """
    Tests a full agentic workflow using the OpenRouter provider via create_llm.
    Mocks LLM behavior to guide the agent through search, scrape, and finish actions.
    """
    load_dotenv()  # Ensure .env is loaded for potential real API key if not mocked

    # Define the sequence of LLM responses (parsed JSON objects) to guide the agent's actions
    mock_agent_llm_json = MagicMock(
        side_effect=[
            # 1. Agent decides to search
            {"tool_name": "search_tool", "arguments": {"query": "future of AI"}},
            # 2. Agent decides to scrape the first URL from search results
            {"tool_name": "scrape_tool", "arguments": {"url": "https://example.com/ai-future"}},
            # 3. Agent decides to scrape the second URL
            {"tool_name": "scrape_tool", "arguments": {"url": "https://example.com/ml-trends"}},
            # 4. Agent decides to finish and provide a summary
            {"tool_name": "finish", "arguments": {"summary": "A comprehensive summary of AI and ML."}},
        ]
    )

    # Set environment variables for OpenRouter (can be real for actual integration, mocked here)
    with patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "google/gemini-pro",
            "LLM_BASE_URL": "https://openrouter.ai/api/v1",
            "OPENROUTER_API_KEY": "mock_openrouter_api_key",
            "OPENROUTER_REFERER": "https://test-app.com",
        },
    ):
        # 1. Create the LLM client using the factory
        llm = create_llm()

        # 2. Instantiate the real ResearchAgent with the LLM and mocked tools
        research_agent = ResearchAgent(llm=llm, search_tool=mock_search_tool, scrape_tool=mock_scraper_tool)

        # Patch the llm_json method of the instantiated research_agent
        research_agent.llm_json = mock_agent_llm_json

        # 3. Define a simple task
        topic = "Future of AI and ML"
        task = MockAbstractTask(agent=research_agent, description=f"Research on: {topic}", expected_output="A summary of the research.")

        # 4. Initialize and run the Runner
        app_runner = MockRunner(
            orchestrator_cls=MockCrewAIOrchestrator,
            agents=[research_agent],
            tasks=[task],
        )

        result = app_runner.run(query=topic)

        # Assertions
        assert "comprehensive summary" in result.lower()
        mock_search_tool.execute.assert_called_once_with(query="future of ai")
        mock_scraper_tool.execute.assert_any_call(url="https://example.com/ai-future")
        mock_scraper_tool.execute.assert_any_call(url="https://example.com/ml-trends")
        assert mock_scraper_tool.execute.call_count == 2

        # Verify that the underlying crewai LLM was called multiple times
        # Here, mock_crew_llm_lib.return_value.call corresponds to the `CrewAILLM(crew_llm).call` method.
        # Since ResearchAgent.llm_json is patched, the CrewAILLM.call method is NOT directly called.
        # Instead, research_agent.llm_json is called.
        # So this assertion should be removed or changed. The important assertion is that the agent's logic flows.
        assert mock_agent_llm_json.call_count == 4


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENROUTER_API_KEY"), reason="OPENROUTER_API_KEY is not set")
@patch.dict(os.environ, {"OPENROUTER_REFERER": "https://agentic-knowledge-base.com/tests"})
def test_openrouter_connectivity(llm_factory):
    """
    Tests basic connectivity to the OpenRouter API and verifies a simple response.
    """
    log.debug("Getting OpenRouter LLM from factory...")
    llm = llm_factory("openrouter", "google/gemma-7b-it", timeout_s=360)
    log.debug("OpenRouter LLM obtained from factory.")

    try:
        log.debug("Calling OpenRouter LLM...")
        response_text = llm.call("Hello, OpenRouter! Respond with just 'Hello' and nothing else.")
        log.debug("OpenRouter LLM call finished.")

        assert response_text is not None
        assert isinstance(response_text, str)
        assert len(response_text.strip()) > 0
        log.debug(f"OpenRouter LLM response: {response_text}")

    except Exception as e:
        pytest.fail(f"OpenRouter connectivity test failed with an unexpected error: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
