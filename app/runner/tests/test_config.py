import os
from unittest.mock import patch

import pytest

# We will create this file and class in the next step
# from runner.config import Settings


def test_settings_loading_from_env():
    """
    Test that the Settings class correctly loads configuration
    from environment variables and performs type casting.
    """
    # Arrange
    env_vars = {
        # LLM Config
        "LLM_MODEL": "test-model-from-env",
        "LLM_PROVIDER": "test-provider-from-env",
        "LLM_BASE_URL": "http://test-llm-url.from.env",
        # Orchestrator Config
        "ORCHESTRATOR_TYPE": "test-orchestrator-from-env",
        # Outline Tool Config
        "OUTLINE_API_KEY": "test_api_key_from_env",
        "OUTLINE_BASE_URL": "http://test.outline.from.env",
        "OUTLINE_COLLECTION_ID": "test_collection_id_from_env",
        # Qdrant Tool Config
        "QDRANT_HOST": "test.qdrant.from.env",
        "QDRANT_GRPC_PORT": "1234",
        "QDRANT_HTTP_PORT": "5678",
    }

    with patch.dict(os.environ, env_vars):
        # Dynamically import here to ensure it uses the patched env
        from runner.config import Settings

        # Act
        settings = Settings()

        # Assert
        assert settings.llm_model == "test-model-from-env"
        assert settings.llm_provider == "test-provider-from-env"
        assert settings.llm_base_url == "http://test-llm-url.from.env"
        assert settings.orchestrator_type == "test-orchestrator-from-env"
        assert settings.outline_api_key == "test_api_key_from_env"
        assert settings.outline_base_url == "http://test.outline.from.env"
        assert settings.outline_collection_id == "test_collection_id_from_env"
        assert settings.qdrant_host == "test.qdrant.from.env"
        assert settings.qdrant_grpc_port == 1234  # Check for correct type casting
        assert settings.qdrant_http_port == 5678  # Check for correct type casting


if __name__ == "__main__":
    pytest.main([__file__])
