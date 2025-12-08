import os
from unittest.mock import patch

import pytest
from agents_core.core import AbstractLLM
from integration_llm.factory import create_llm


@patch("crewai.LLM")
def test_create_llm_ollama_provider_default_url(mock_crew_llm):
    """Test that create_llm correctly uses the default URL for Ollama when LLM_BASE_URL is not set."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model", "LLM_BASE_URL": "http://localhost:11434"}):
        llm_instance = create_llm(orchestrator_type="crew_ai")

        assert isinstance(llm_instance, AbstractLLM)
        mock_crew_llm.assert_called_once_with(model="test-model", base_url="http://localhost:11434", timeout=300, api_key=None)


@patch("crewai.LLM")
def test_create_llm_ollama_provider_custom_url(mock_crew_llm):
    """Test that create_llm correctly uses a custom LLM_BASE_URL for Ollama."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model", "LLM_BASE_URL": "https://custom-ollama:12345"}):
        create_llm(orchestrator_type="crew_ai")
        mock_crew_llm.assert_called_once_with(model="test-model", base_url="https://custom-ollama:12345", timeout=300, api_key=None)


@patch("crewai.LLM")
def test_create_llm_openrouter_provider(mock_crew_llm):
    """Test that create_llm correctly creates an OpenRouter client."""
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openrouter", "LLM_MODEL": "test-model", "OPENROUTER_API_KEY": "test-key", "OPENROUTER_REFERER": "https://test.app", "LLM_BASE_URL": "https://openrouter.ai/api/v1"},
    ):
        llm_instance = create_llm(orchestrator_type="crew_ai", timeout_s=300)

        assert isinstance(llm_instance, AbstractLLM)
        mock_crew_llm.assert_called_once_with(
            model="test-model",
            timeout=300,
            base_url="https://openrouter.ai/api/v1",
            api_key="test-key",
            extra_headers={"HTTP-Referer": "https://test.app"},
        )


def test_create_llm_openrouter_missing_key():
    """Test that create_llm raises an error if the OpenRouter API key is missing."""
    with (
        patch.dict(os.environ, {"LLM_PROVIDER": "openrouter", "LLM_MODEL": "test-model", "LLM_BASE_URL": "https://openrouter.ai/api/v1"}, clear=True),
        pytest.raises(ValueError, match="OPENROUTER_API_KEY must be set in the environment or passed as arguments."),
    ):
        create_llm(orchestrator_type="crew_ai")


def test_create_llm_unsupported_provider():
    """Test that create_llm raises an error for an unsupported provider."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "unsupported", "LLM_MODEL": "test-model"}), pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
        create_llm(orchestrator_type="crew_ai")


def test_create_llm_unsupported_orchestrator_type():
    """Test that create_llm raises an error for an unsupported orchestrator type."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model"}), pytest.raises(ValueError, match="Unsupported orchestrator type: not_an_orchestrator"):
        create_llm(orchestrator_type="not_an_orchestrator")


def test_create_llm_missing_provider():
    """Test that create_llm raises an error if provider and model are not specified."""
    with patch.dict(os.environ, {}, clear=True), pytest.raises(ValueError, match="LLM_PROVIDER must be set in the environment or passed as arguments."):
        create_llm(orchestrator_type="crew_ai")


def test_create_llm_missing_model():
    """Test that create_llm raises an error if provider and model are not specified."""
    with patch.dict(os.environ, {}, clear=True), pytest.raises(ValueError, match="LLM_MODEL must be set in the environment or passed as arguments."):
        create_llm(provider="ollama", orchestrator_type="crew_ai")


@patch("crewai.LLM")
def test_create_llm_uses_arguments_over_env(mock_crew_llm):
    """Test that create_llm prioritizes arguments over environment variables."""
    with patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "env-model",
            "LLM_BASE_URL": "https://should-be-ignored.com",
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_REFERER": "https://test.app",
        },
    ):
        create_llm(orchestrator_type="crew_ai", provider="openrouter", model="arg-model", base_url="https://openrouter.ai/api/v1", timeout_s=300)
        mock_crew_llm.assert_called_once_with(
            model="arg-model",
            timeout=300,
            base_url="https://openrouter.ai/api/v1",
            api_key="test-key",
            extra_headers={"HTTP-Referer": "https://test.app"},
        )


if __name__ == "__main__":
    pytest.main([__file__])
