import os

import pytest
import structlog

log = structlog.get_logger()


@pytest.mark.integration
def test_llm_connectivity(llm_factory):
    """
    Tests basic connectivity to the configured real LLM and verifies a simple response.
    """
    log.debug("Getting LLM from factory...")
    llm = llm_factory("qwen2:0.5b")
    log.debug("LLM obtained from factory.")
    log.debug(f"Testing LLM connectivity with provider: {os.getenv('INTEGRATION_TEST_LLM_PROVIDER', 'mock')}")

    try:
        log.debug("Calling LLM...")
        response_text = llm.call("Hello, LLM! Respond with just 'Hello' and nothing else.")
        log.debug("LLM call finished.")

        assert response_text is not None
        assert isinstance(response_text, str)
        assert len(response_text.strip()) > 0
        log.debug(f"LLM response: {response_text}")

    except Exception as e:
        pytest.fail(f"LLM connectivity test failed with an unexpected error: {e}")
