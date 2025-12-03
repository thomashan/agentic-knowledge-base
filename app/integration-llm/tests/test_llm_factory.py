import os
from unittest.mock import Mock, patch

import pytest
import requests.exceptions
from agents_core.core import AbstractLLM
from integration_llm.factory import check_openrouter_health, create_llm


@patch("crewai.LLM")
def test_create_llm_ollama_provider_default_url(mock_crew_llm):
    """Test that create_llm correctly uses the default URL for Ollama when LLM_BASE_URL is not set."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model"}):
        llm_instance = create_llm(orchestrator_type="crew_ai")  # Added orchestrator_type

        assert isinstance(llm_instance, AbstractLLM)
        # Updated assertion: removed "ollama/" prefix, added timeout_s and api_key=None
        mock_crew_llm.assert_called_once_with(model="test-model", base_url="http://localhost:11434", timeout_s=300, api_key=None)


@patch("crewai.LLM")
def test_create_llm_ollama_provider_custom_url(mock_crew_llm):
    """Test that create_llm correctly uses a custom LLM_BASE_URL for Ollama."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model", "LLM_BASE_URL": "http://custom-ollama:12345"}):
        create_llm(orchestrator_type="crew_ai")  # Added orchestrator_type
        # Updated assertion: removed "ollama/" prefix, added timeout_s and api_key=None
        mock_crew_llm.assert_called_once_with(model="test-model", base_url="http://custom-ollama:12345", timeout_s=300, api_key=None)


@patch("crewai.LLM")
def test_create_llm_openrouter_provider(mock_crew_llm):
    """Test that create_llm correctly creates an OpenRouter client."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "openrouter", "LLM_MODEL": "test-model", "OPENROUTER_API_KEY": "test-key", "OPENROUTER_REFERER": "http://test.app"}):
        llm_instance = create_llm(orchestrator_type="crew_ai")  # Added orchestrator_type

        assert isinstance(llm_instance, AbstractLLM)
        # Updated assertion: added timeout_s
        mock_crew_llm.assert_called_once_with(
            model="test-model",
            base_url="https://openrouter.ai/api/v1",
            api_key="test-key",
            timeout_s=300,  # Added timeout_s
            extra_headers={"HTTP-Referer": "http://test.app"},
        )


def test_create_llm_openrouter_missing_key():
    """Test that create_llm raises an error if the OpenRouter API key is missing."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "openrouter", "LLM_MODEL": "test-model"}, clear=True), pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable is not set."):
        create_llm(orchestrator_type="crew_ai")  # Added orchestrator_type


def test_create_llm_unsupported_provider():
    """Test that create_llm raises an error for an unsupported provider."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "unsupported", "LLM_MODEL": "test-model"}), pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
        create_llm(orchestrator_type="crew_ai")  # Added orchestrator_type


def test_create_llm_unsupported_orchestrator_type():
    """Test that create_llm raises an error for an unsupported orchestrator type."""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "LLM_MODEL": "test-model"}), pytest.raises(ValueError, match="Unsupported orchestrator type: not_an_orchestrator"):
        create_llm(orchestrator_type="not_an_orchestrator")


def test_create_llm_missing_provider_and_model():
    """Test that create_llm raises an error if provider and model are not specified."""
    with patch.dict(os.environ, {}, clear=True), pytest.raises(ValueError, match="LLM_PROVIDER and LLM_MODEL must be set"):
        create_llm(orchestrator_type="crew_ai")  # Added orchestrator_type


@patch("crewai.LLM")
def test_create_llm_uses_arguments_over_env(mock_crew_llm):
    """Test that create_llm prioritizes arguments over environment variables."""
    with patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "env-model",
            "LLM_BASE_URL": "http://should-be-ignored.com",
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_REFERER": "https://test.app",
        },
    ):
        create_llm(orchestrator_type="crew_ai", provider="openrouter", model="arg-model")  # Added orchestrator_type
        # Updated assertion: added timeout_s
        mock_crew_llm.assert_called_once_with(
            model="arg-model",
            base_url="https://openrouter.ai/api/v1",
            api_key="test-key",
            timeout_s=300,  # Added timeout_s
            extra_headers={"HTTP-Referer": "https://test.app"},
        )


# Tests for check_openrouter_health
@patch("integration_llm.factory.requests.get")
def test_check_openrouter_health_success(mock_get):
    """Test successful OpenRouter health check."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with patch.dict(os.environ, {"LLM_BASE_URL": "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY": "test-key", "OPENROUTER_REFERER": "https://test.app"}):
        assert check_openrouter_health() is True
        mock_get.assert_called_once_with("https://openrouter.ai/api/v1/models", headers={"Authorization": "Bearer test-key", "HTTP-Referer": "https://test.app"}, timeout=5)


def test_check_openrouter_health_missing_base_url():
    """Test missing LLM_BASE_URL for OpenRouter health check."""
    with (
        patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key", "OPENROUTER_REFERER": "https://test.app"}, clear=True),
        pytest.raises(ValueError, match="LLM_BASE_URL environment variable is not set for OpenRouter health check."),
    ):
        check_openrouter_health()


def test_check_openrouter_health_incorrect_base_url():
    """Test incorrect LLM_BASE_URL for OpenRouter health check."""
    with (
        patch.dict(os.environ, {"LLM_BASE_URL": "http://wrong-url.com", "OPENROUTER_API_KEY": "test-key", "OPENROUTER_REFERER": "https://test.app"}, clear=True),
        pytest.raises(ValueError, match="LLM_BASE_URL must be 'https://openrouter.ai/api/v1' for OpenRouter health check."),
    ):
        check_openrouter_health()


def test_check_openrouter_health_missing_api_key():
    """Test missing OPENROUTER_API_KEY for OpenRouter health check."""
    with (
        patch.dict(os.environ, {"LLM_BASE_URL": "https://openrouter.ai/api/v1", "OPENROUTER_REFERER": "https://test.app"}, clear=True),
        pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable is not set for OpenRouter health check."),
    ):
        check_openrouter_health()


def test_check_openrouter_health_missing_referer():
    """Test missing OPENROUTER_REFERER for OpenRouter health check."""
    with (
        patch.dict(os.environ, {"LLM_BASE_URL": "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY": "test-key"}, clear=True),
        pytest.raises(ValueError, match="OPENROUTER_REFERER environment variable is not set for OpenRouter health check."),
    ):
        check_openrouter_health()


@patch("integration_llm.factory.requests.get")
def test_check_openrouter_health_http_error(mock_get):
    """Test HTTP error during OpenRouter health check."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Unauthorized", response=mock_response)
    mock_get.return_value = mock_response

    with patch.dict(os.environ, {"LLM_BASE_URL": "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY": "test-key", "OPENROUTER_REFERER": "https://test.app"}):
        assert check_openrouter_health() is False
        mock_get.assert_called_once()


@patch("integration_llm.factory.requests.get")
def test_check_openrouter_health_connection_error(mock_get):
    """Test connection error during OpenRouter health check."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

    with patch.dict(os.environ, {"LLM_BASE_URL": "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY": "test-key", "OPENROUTER_REFERER": "https://agentic-knowledge-base.com"}):
        assert check_openrouter_health() is False
        mock_get.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
