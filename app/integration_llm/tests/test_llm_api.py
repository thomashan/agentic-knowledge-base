import os
import litellm

import pytest


@pytest.mark.integration
def test_llm_connectivity(real_llm_client):
    """
    Tests basic connectivity to the configured real LLM and verifies a simple response.
    This test will use the LLM client provided by the real_llm_client fixture.
    """
    print(f"\nTesting LLM connectivity with provider: {os.getenv('INTEGRATION_TEST_LLM_PROVIDER', 'mock')}")  # noqa: T201

    # This part needs to be adapted based on the actual LLM client's API
    # For CrewAI-compatible LLMs (MockCrewAILLM):
    try:
        response = litellm.completion(model="custom_llm", custom_llm_provider=real_llm_client, messages=[{"role": "user", "content": "Hello, LLM!"}])
        response_text = response.choices[0].message.content
        assert response_text is not None
        print(f"MockCrewAILLM response: {response_text}")  # noqa: T201
    except Exception as e:
        pytest.fail(f"MockCrewAILLM connectivity test failed: {e}")
