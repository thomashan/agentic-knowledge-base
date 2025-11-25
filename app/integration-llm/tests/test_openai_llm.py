from unittest.mock import MagicMock

import pytest
from agents_core.core import AbstractLLM


def test_openai_llm_is_abstract_llm():
    """
    Tests that OpenAiLLM is an instance of AbstractLLM.
    """
    # RED: This will fail because OpenAiLLM doesn't exist yet.
    from integration_llm.openai import OpenAiLLM

    llm = OpenAiLLM(model="gpt-4", api_key="test-key")
    assert isinstance(llm, AbstractLLM)


def test_openai_llm_call_method(mocker):
    """
    Tests that the call method of OpenAiLLM makes the correct API request.
    """
    # Arrange
    from integration_llm.openai import OpenAiLLM

    # Mock the OpenAI client
    mock_openai_client = MagicMock()
    mock_chat_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "test response"
    mock_chat_completion.choices = [mock_choice]
    mock_openai_client.chat.completions.create.return_value = mock_chat_completion

    mocker.patch("openai.OpenAI", return_value=mock_openai_client)

    llm = OpenAiLLM(model="gpt-4", api_key="test-key")

    # Act
    response = llm.call("test prompt")

    # Assert
    mock_openai_client.chat.completions.create.assert_called_once_with(model="gpt-4", messages=[{"role": "user", "content": "test prompt"}])
    assert response == "test response"


if __name__ == "__main__":
    pytest.main()
