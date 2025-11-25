from unittest.mock import MagicMock

import pytest
from agents_core.core import AbstractLLM


def test_ollama_llm_is_abstract_llm():
    """
    Tests that OllamaLLM is an instance of AbstractLLM.
    """
    from integration_llm.ollama import OllamaLLM

    llm = OllamaLLM(model="test-model", base_url="http://localhost:11434")
    assert isinstance(llm, AbstractLLM)


def test_ollama_llm_call_method(mocker):
    """
    Tests that the call method of OllamaLLM makes the correct HTTP request.
    """
    # Arrange
    from integration_llm.ollama import OllamaLLM

    mock_post = mocker.patch("requests.post")
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "test response"}
    mock_post.return_value = mock_response

    llm = OllamaLLM(model="test-model", base_url="http://localhost:11434")

    # Act
    response = llm.call("test prompt")

    # Assert
    mock_post.assert_called_once_with("http://localhost:11434/api/generate", json={"model": "test-model", "prompt": "test prompt", "stream": False})
    assert response == "test response"


if __name__ == "__main__":
    pytest.main()
