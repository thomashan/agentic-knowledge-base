import os
from unittest.mock import Mock

import pytest

# Placeholder for a real LLM client.
# In a real scenario, you would instantiate your LLM client here
# based on configuration (e.g., environment variables).
# For demonstration, we'll use a mock, but the intention is to replace
# this with a real client for actual integration tests.


@pytest.fixture(scope="session")
def real_llm_client():
    """
    Fixture to provide a configured real LLM client for integration tests.
    This client should be configured to connect to an actual LLM service.
    """
    # Example: Using an environment variable to determine which LLM to use
    llm_provider = os.getenv("INTEGRATION_TEST_LLM_PROVIDER", "mock")

    if llm_provider == "openai":
        # from openai import OpenAI
        # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # return client
        print("Using OpenAI LLM client (placeholder)")  # noqa: T201
        mock_client = Mock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Mocked OpenAI response"
        return mock_client
    elif llm_provider == "gemini":
        # import google.generativeai as genai
        # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # model = genai.GenerativeModel('gemini-pro')
        # return model
        print("Using Gemini LLM client (placeholder)")  # noqa: T201
        mock_client = Mock()
        mock_client.generate_content.return_value.text = "Mocked Gemini response"
        return mock_client
    else:
        # Default to a mock client for local development or if no provider is specified
        print("Using Mock LLM client for integration tests. Set INTEGRATION_TEST_LLM_PROVIDER to 'openai' or 'gemini' for real LLM tests.")  # noqa: T201
        mock_client = Mock()
        mock_client.generate_content.return_value.text = "Mocked LLM response from conftest"
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Mocked LLM response from conftest"
        return mock_client


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
    return {"client": real_llm_client, "model": "test-model"}
