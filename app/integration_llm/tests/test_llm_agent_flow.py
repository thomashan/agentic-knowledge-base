import os
from typing import Any
from unittest.mock import Mock

import pytest
from agents_core.core import AbstractAgent, AbstractTask, AbstractTool, ExecutionResult
from crewai_adapter.adapter import CrewAIOrchestrator


# Define a mock tool for testing purposes
class MockSearchTool(AbstractTool):
    name: str = "search_tool"
    description: str = "A tool to search the internet for information."

    def execute(self, query: str) -> str:
        if "AI trends" in query:
            return "Latest AI trends: Generative AI, Large Language Models, AI Ethics."
        return f"Search result for: {query}"


# Define a mock agent that uses the real LLM client
class RealLLMAgent(AbstractAgent):
    def __init__(self, llm_client: Mock):
        self._llm_client = llm_client

    @property
    def role(self) -> str:
        return "Integration Test Agent"

    @property
    def goal(self) -> str:
        return "Verify end-to-end agent flow with a real LLM."

    @property
    def backstory(self) -> str:
        return "An agent dedicated to testing LLM integrations."

    @property
    def tools(self) -> list[AbstractTool]:
        return [MockSearchTool()]

    @property
    def llm_config(self) -> dict[str, Any] | None:
        # Pass the real LLM client directly or its configuration
        return {"client": self._llm_client}


# Define a mock task
class RealLLMTask(AbstractTask):
    def __init__(self, agent: AbstractAgent):
        self._agent = agent

    @property
    def description(self) -> str:
        return "Research the latest AI trends using the search tool."

    @property
    def expected_output(self) -> str:
        return "A summary of the latest AI trends."

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list["AbstractTask"] | None:
        return None


@pytest.mark.integration
def test_llm_agent_flow_with_real_llm(real_llm_client):
    """
    Tests an end-to-end agent flow using the CrewAIOrchestrator with a real LLM.
    This test verifies that the orchestrator can correctly set up agents and tasks
    that interact with a real LLM and potentially use tools.
    """
    print(f"\nTesting LLM agent flow with provider: {os.getenv('INTEGRATION_TEST_LLM_PROVIDER', 'mock')}")  # noqa: T201

    # Instantiate the agent with the real LLM client
    agent = RealLLMAgent(llm_client=real_llm_client)
    task = RealLLMTask(agent=agent)

    # Configure the orchestrator to use the real LLM (if CrewAI needs it directly)
    # Note: CrewAI typically takes LLM config per agent, but if there's a global config,
    # it would go here. For now, we rely on the agent's llm_config.
    orchestrator_config = {
        "process": "sequential",
        "verbose": True,
        # "manager_llm": real_llm_client, # If using hierarchical process and manager_llm is needed
    }
    orchestrator = CrewAIOrchestrator(config=orchestrator_config)

    orchestrator.add_agent(agent)
    orchestrator.add_task(task)

    try:
        result: ExecutionResult = orchestrator.execute()

        assert result.raw_output is not None
        assert "AI trends" in result.raw_output or "Generative AI" in result.raw_output
        print(f"Agent Flow Raw Output: {result.raw_output}")  # noqa: T201

    except Exception as e:
        pytest.fail(f"LLM agent flow integration test failed: {e}")
