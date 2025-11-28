import os
import pytest
import structlog
from crewai import LLM

log = structlog.get_logger()

@pytest.mark.integration
def test_openrouter_connectivity(llm_factory):
    """
    Tests basic connectivity to the OpenRouter API and verifies a simple response.
    """
    log.debug("Getting OpenRouter LLM from factory...")
    llm = llm_factory(
        model_name="google/gemma-7b-it", 
        provider="openrouter", 
        timeout_s=360
    )
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
    pytest.main()
