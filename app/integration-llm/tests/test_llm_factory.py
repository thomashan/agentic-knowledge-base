import pytest
from integration_llm.ollama import OllamaLLM
from integration_llm.openai import OpenAiLLM  # New import


def test_llm_factory_can_create_ollama_llm():
    """
    Tests that the LlmFactory can create an instance of OllamaLLM.
    """
    from integration_llm.factory import LlmFactory

    config = {"provider": "ollama", "model": "test-model", "base_url": "http://localhost:11434"}

    llm = LlmFactory.create_llm(config)

    assert isinstance(llm, OllamaLLM)
    assert llm.model == "test-model"
    assert llm.base_url == "http://localhost:11434"


def test_llm_factory_can_create_openai_llm():
    """
    Tests that the LlmFactory can create an instance of OpenAiLLM.
    """
    from integration_llm.factory import LlmFactory

    config = {"provider": "openai", "model": "gpt-4", "api_key": "test-api-key"}

    llm = LlmFactory.create_llm(config)

    assert isinstance(llm, OpenAiLLM)
    assert llm.model == "gpt-4"
    assert llm.client.api_key == "test-api-key"


def test_llm_factory_raises_error_for_unknown_provider():
    """
    Tests that the LlmFactory raises a ValueError for an unknown provider.
    """
    from integration_llm.factory import LlmFactory

    config = {"provider": "unknown"}

    with pytest.raises(ValueError, match="Unknown LLM provider: unknown"):
        LlmFactory.create_llm(config)


if __name__ == "__main__":
    pytest.main()
