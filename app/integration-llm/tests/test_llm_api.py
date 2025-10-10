import os

import pytest


@pytest.mark.integration
def test_llm_connectivity(llm):
    """
    Tests basic connectivity to the configured real LLM and verifies a simple response.
    """
    print(f"\nTesting LLM connectivity with provider: {os.getenv('INTEGRATION_TEST_LLM_PROVIDER', 'mock')}")  # noqa: T201

    try:
        response_text = llm.call("Hello, LLM! Respond with just 'Hello' and nothing else.")

        assert response_text is not None
        assert isinstance(response_text, str)
        assert len(response_text.strip()) > 0
        print(f"LLM response: {response_text}")  # noqa: T201

    except Exception as e:
        pytest.fail(f"LLM connectivity test failed with an unexpected error: {e}")
