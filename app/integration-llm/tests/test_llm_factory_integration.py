import os

import pytest
import structlog
from crewai import LLM

log = structlog.get_logger()


@pytest.mark.integration
@pytest.mark.parametrize("provider_model", ["ollama/gemma2:2b", "openrouter/google/gemma-7b-it"])
def test_llm_factory_creation(llm_factory, provider_model):
    """
    Tests that the llm_factory can correctly create LLM instances for different providers.
    """
    if "openrouter" in provider_model and not (
        # Check if environment variables for OpenRouter are set
        os.getenv("OPENROUTER_API_KEY") and os.getenv("LLM_BASE_URL")
    ):
        pytest.skip("OpenRouter environment variables not set.")

    llm_instance = llm_factory(provider_model, timeout_s=360)
    assert isinstance(llm_instance, LLM)
    log.info(f"Successfully created LLM for {provider_model}")


if __name__ == "__main__":
    pytest.main()
