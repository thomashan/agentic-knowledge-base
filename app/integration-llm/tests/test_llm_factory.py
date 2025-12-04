from unittest.mock import patch

import pytest
from agents_core.core import AbstractLLM
from integration_llm.factory import create_llm


def create_getenv_side_effect(vars_to_mock: dict):
    """Factory for creating a side_effect function for patching os.getenv."""

    def side_effect(key, default=None):
        return vars_to_mock.get(key, default)

    return side_effect


@patch("crewai.LLM")
@patch("integration_llm.factory.os.getenv")
def test_create_llm_ollama_provider_default_url(mock_getenv, mock_crew_llm):
    """Test that create_llm correctly uses the default URL for Ollama when LLM_BASE_URL is not set."""
    mock_getenv.side_effect = create_getenv_side_effect({"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model"})

    llm_instance = create_llm()
    assert isinstance(llm_instance, AbstractLLM)
    mock_crew_llm.assert_called_once_with(model="test-model", base_url="http://localhost:11434", timeout_s=300, api_key=None, custom_llm_provider="ollama")


@patch("crewai.LLM")
@patch("integration_llm.factory.os.getenv")
def test_create_llm_ollama_provider_custom_url(mock_getenv, mock_crew_llm):
    """Test that create_llm correctly uses a custom LLM_BASE_URL for Ollama."""
    mock_getenv.side_effect = create_getenv_side_effect({"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model", "LLM_BASE_URL": "http://custom-ollama:12345"})
    create_llm()
    mock_crew_llm.assert_called_once_with(model="test-model", base_url="http://custom-ollama:12345", timeout_s=300, api_key=None, custom_llm_provider="ollama")


@patch("integration_llm.factory.llm_factory")
@patch("integration_llm.factory.os.getenv")
def test_create_llm_openrouter_provider_respects_base_url_arg(mock_getenv, mock_llm_factory):
    """Test create_llm passes the correct base_url for openrouter, prioritizing function arg."""
    mock_getenv.side_effect = create_getenv_side_effect({"LLM_PROVIDER": "openrouter", "LLM_MODEL": "test-model", "OPENROUTER_API_KEY": "test-key"})
    create_llm(base_url="https://arg-url.com/v1")
    mock_llm_factory.assert_called_once()
    _, call_kwargs = mock_llm_factory.call_args
    assert call_kwargs.get("base_url") == "https://arg-url.com/v1"


@patch("integration_llm.factory.llm_factory")
@patch("integration_llm.factory.os.getenv")
def test_create_llm_openrouter_provider_respects_env_base_url(mock_getenv, mock_llm_factory):
    """Test create_llm passes the correct base_url for openrouter from env var."""
    mock_getenv.side_effect = create_getenv_side_effect(
        {
            "LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "test-model",
            "OPENROUTER_API_KEY": "test-key",
            "LLM_BASE_URL": "https://env-url.com/v1",
        }
    )
    create_llm()
    mock_llm_factory.assert_called_once()
    _, call_kwargs = mock_llm_factory.call_args
    assert call_kwargs.get("base_url") == "https://env-url.com/v1"


@patch("integration_llm.factory.os.getenv")
def test_create_llm_openrouter_missing_key(mock_getenv):
    """Test that create_llm raises an error if the OpenRouter API key is missing."""
    mock_getenv.side_effect = create_getenv_side_effect({"LLM_PROVIDER": "openrouter", "LLM_MODEL": "test-model"})
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable is not set."):
        create_llm()


@patch("integration_llm.factory.os.getenv")
def test_create_llm_unsupported_provider(mock_getenv):
    """Test that create_llm raises an error for an unsupported provider."""
    mock_getenv.side_effect = create_getenv_side_effect({"LLM_PROVIDER": "unsupported", "LLM_MODEL": "test-model"})
    with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
        create_llm()


@patch("integration_llm.factory.os.getenv")
def test_create_llm_unsupported_orchestrator_type(mock_getenv):
    """Test that create_llm raises an error for an unsupported orchestrator type."""
    mock_getenv.side_effect = create_getenv_side_effect({"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model"})
    with pytest.raises(ValueError, match="Unsupported orchestrator type: not_an_orchestrator"):
        create_llm(orchestrator_type="not_an_orchestrator")


@patch("integration_llm.factory.os.getenv")
def test_create_llm_missing_provider_and_model(mock_getenv):
    """Test that create_llm raises an error if provider and model are not specified."""
    mock_getenv.side_effect = create_getenv_side_effect({})  # No env vars
    with pytest.raises(ValueError, match="LLM_PROVIDER and LLM_MODEL must be set"):
        create_llm()


if __name__ == "__main__":
    pytest.main([__file__])
