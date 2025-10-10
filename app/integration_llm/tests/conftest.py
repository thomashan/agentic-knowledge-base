import os
from typing import Any, List, Optional
from unittest.mock import Mock

import pytest
from langchain_core.language_models.llms import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult


class MockCrewAILLM:
    """A mock LLM that mimics a crewai compatible LLM."""
    mock_response: str = "Mocked LLM response"
    stop: list[str] = []

    def __init__(self, mock_response: str = "Mocked LLM response", **kwargs: Any):
        self.mock_response = mock_response

    def __call__(self, *args, **kwargs):
        return self.mock_response

    def supports_stop_words(self) -> bool:
        return True


@pytest.fixture(scope="session")
def real_llm_client():
    """
    Fixture to provide a configured real LLM client for integration tests.
    This client should be configured to connect to an actual LLM service.
    """
    # Example: Using an environment variable to determine which LLM to use
    llm_provider = os.getenv("INTEGRATION_TEST_LLM_PROVIDER", "mock")

    if llm_provider == "openai":
        print("Using OpenAI LLM client (placeholder)")  # noqa: T201
        mock_llm_instance = MockCrewAILLM(mock_response="Mocked OpenAI response")
        return mock_llm_instance
    elif llm_provider == "gemini":
        print("Using Gemini LLM client (placeholder)")  # noqa: T201
        mock_llm_instance = MockCrewAILLM(mock_response="Mocked Gemini response")
        return mock_llm_instance
    elif llm_provider == "local":
        local_llm_endpoint = os.getenv("LOCAL_LLM_ENDPOINT")
        if not local_llm_endpoint:
            pytest.fail("LOCAL_LLM_ENDPOINT environment variable not set for local LLM provider.")
        print(f"Using Local LLM client (placeholder) at {local_llm_endpoint}")  # noqa: T201
        mock_llm_instance = MockCrewAILLM(mock_response=f"Mocked local LLM response from {local_llm_endpoint}")
        return mock_llm_instance
    else:
        print("Using Mock LLM client for integration tests. Set INTEGRATION_TEST_LLM_PROVIDER to 'openai' or 'gemini' for real LLM tests.")  # noqa: T201
        mock_llm_instance = MockCrewAILLM(mock_response="Mocked LLM response from conftest")
        return mock_llm_instance


@pytest.fixture
def llm_config(real_llm_client):
    """
    Fixture to provide an LLM configuration dictionary suitable for
    passing to AbstractAgent or CrewAIOrchestrator.
    """
    # This would typically return a dictionary that CrewAI or your
    # AbstractAgent can use to instantiate or reference the LLM.
    # For a real LLM, this might involve passing the client object directly
    # or configuration parameters that allow the agent to instantiate it.
    return {"client": real_llm_client}