import os

import litellm
import pytest
import structlog

log = structlog.get_logger()


@pytest.mark.integration
def test_ollama_llm_connectivity(llm_factory):
    """
    Tests basic connectivity to the configured real LLM and verifies a simple response.
    """
    log.debug("Getting LLM from factory...")
    # Modified llm_factory call to explicitly pass model_name and provider
    llm = llm_factory(model_name="ollama/gemma2:2b", provider="ollama", timeout_s=360)
    log.debug("LLM obtained from factory.")
    # Changed to use LLM_PROVIDER env var for clarity
    log.debug(f"Testing LLM connectivity with provider: {os.getenv('LLM_PROVIDER', 'mock')}")

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


@pytest.mark.integration
def test_ollama_llm_timeout(llm_factory):
    """
    Tests that the LLM call times out as expected.
    """
    # Create an LLM with a very short timeout
    # Modified llm_factory call to explicitly pass model_name and provider
    llm = llm_factory(model_name="ollama/gemma2:2b", provider="ollama", timeout_s=0.001)

    with pytest.raises(litellm.exceptions.APIConnectionError):
        llm.call("This is a test prompt.")


@pytest.mark.integration
def test_ollama_llm_connection_refused(llm_factory):
    """
    Tests that the LLM call raises a connection error when the server is not running.
    """
    # Create an LLM with a base_url that is not listening
    # Modified llm_factory call to explicitly pass model_name and provider
    llm = llm_factory(model_name="ollama/gemma2:2b", provider="ollama", base_url="http://localhost:12345")

    with pytest.raises(litellm.exceptions.APIConnectionError):
        llm.call("This is a test prompt.")


if __name__ == "__main__":
    pytest.main([__file__])
