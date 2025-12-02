from unittest.mock import MagicMock

import pytest
from agents_core.core import AbstractAgent, LLMError


class ConcreteAgent(AbstractAgent):
    """A concrete implementation of AbstractAgent for testing purposes."""

    def __init__(self, llm, max_retries_val=3):
        self._llm = llm
        self._max_retries = max_retries_val

    @property
    def role(self) -> str:
        return "Test Role"

    @property
    def goal(self) -> str:
        return "Test Goal"

    @property
    def backstory(self) -> str:
        return "Test Backstory"

    @property
    def prompt_template(self) -> str | None:
        return "Test Prompt"

    @property
    def tools(self) -> list | None:
        return None

    @property
    def llm_config(self) -> dict | None:
        return None

    @property
    def llm(self):
        return self._llm

    @property
    def max_retries(self) -> int:
        return self._max_retries


def test_llm_json_retries_on_bad_json():
    """
    Tests that the llm_json method retries when the LLM returns malformed JSON.
    """
    # Arrange
    mock_llm = MagicMock()
    bad_json_response = "This is not valid JSON"
    good_json_response = '{"key": "value"}'

    # Mock the behavior of the llm's call method
    mock_llm.call.side_effect = [bad_json_response, good_json_response]

    agent_instance = ConcreteAgent(llm=mock_llm, max_retries_val=3)

    # Act
    result = agent_instance.llm_json("Test prompt")

    # Assert
    assert mock_llm.call.call_count == 2
    assert result == {"key": "value"}


def test_llm_json_fails_after_max_retries():
    """
    Tests that llm_json raises an LLMError after exhausting all retries with bad JSON.
    """
    # Arrange
    mock_llm = MagicMock()
    bad_json_response = "This is consistently bad JSON"

    # Mock the behavior of the llm's call method
    mock_llm.call.return_value = bad_json_response

    agent_instance = ConcreteAgent(llm=mock_llm, max_retries_val=3)

    # Act & Assert
    with pytest.raises(LLMError, match="Failed to parse LLM response as JSON after 3 attempts."):
        agent_instance.llm_json("Test prompt")

    assert mock_llm.call.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])
