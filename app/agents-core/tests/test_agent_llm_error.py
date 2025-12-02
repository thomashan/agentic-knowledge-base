from typing import Any

import pytest
from agents_core.core import AbstractAgent, AbstractLLM, AbstractTool, LLMError

# A mock LLM class for testing purposes


class MockLLM(AbstractLLM):
    def __init__(self, fail_count=0):
        self.fail_count = fail_count
        self.call_count = 0

    def call(self, prompt):
        self.call_count += 1
        if self.call_count <= self.fail_count:
            raise Exception("Connection timed out")
        return "Mock response"


# A simple concrete implementation of AbstractAgent for testing


class SimpleAgent(AbstractAgent):
    def __init__(self, llm: AbstractLLM, max_retries: int = 1):
        self._llm = llm
        self._max_retries = max_retries

    def run(self):
        return self.call_llm("test prompt")

    @property
    def llm(self) -> AbstractLLM:
        return self._llm

    @property
    def role(self) -> str:
        return "Test Agent"

    @property
    def goal(self) -> str:
        return "Test goal"

    @property
    def backstory(self) -> str:
        return "Test backstory"

    @property
    def prompt_template(self) -> str | None:
        return "Test prompt template"

    @property
    def tools(self) -> list[AbstractTool] | None:
        return None

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    @property
    def max_retries(self) -> int:
        return self._max_retries


def test_llm_retry_succeeds():
    """Tests that the LLM call succeeds after a few retries."""
    # Arrange
    mock_llm = MockLLM(fail_count=2)
    agent = SimpleAgent(llm=mock_llm, max_retries=3)

    # Act
    response = agent.run()

    # Assert
    assert response == "Mock response"
    assert mock_llm.call_count == 3


def test_llm_retry_fails():
    """Tests that the LLM call fails after all retries are exhausted."""
    # Arrange
    mock_llm = MockLLM(fail_count=1)
    agent = SimpleAgent(llm=mock_llm)

    # Act & Assert
    with pytest.raises(LLMError, match="Connection timed out"):
        agent.run()
    assert mock_llm.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
