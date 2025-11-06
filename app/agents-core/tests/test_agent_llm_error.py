from typing import Any

import pytest
from agents_core.core import AbstractAgent, AbstractTool, LLMError

# A mock LLM class for testing purposes


class MockLLM:
    def __init__(self, should_timeout=False):
        self.should_timeout = should_timeout

    def call(self, prompt):
        if self.should_timeout:
            raise LLMError("Connection timed out")

        return "Mock response"


# A simple concrete implementation of AbstractAgent for testing


class SimpleAgent(AbstractAgent):
    def __init__(self, llm):
        self.llm = llm

    def run(self):
        return self.llm.call("test prompt")

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


def test_agent_handles_llm_timeout():
    """

    Tests that an agent correctly propagates a timeout error from the LLM.

    """

    # Arrange
    mock_llm = MockLLM(should_timeout=True)
    agent = SimpleAgent(llm=mock_llm)

    # Act & Assert
    with pytest.raises(LLMError, match="Connection timed out"):
        agent.run()
