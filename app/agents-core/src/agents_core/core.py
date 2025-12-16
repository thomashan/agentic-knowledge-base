import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

import structlog
from pydantic import BaseModel, Field

from agents_core.json_utils import to_json_object

L = TypeVar("L")


class AbstractLLM[L](ABC):
    """Abstract interface for a Language Model."""

    @abstractmethod
    def call(self, prompt: str) -> str:
        """Calls the LLM with a given prompt and returns the response."""
        pass

    @property
    @abstractmethod
    def llm(self) -> L:
        pass


class CoreError(Exception):
    """Base exception for the core module."""

    pass


class LLMError(CoreError):
    """Base exception for LLM related errors."""

    pass


class TaskExecutionRecord(BaseModel):
    """A record of the output from a single task execution."""

    task_description: str = Field(..., description="The original description of the task.")
    raw_output: str = Field(..., description="The raw string output of the task.")
    structured_output: Any | None = Field(None, description="Structured output, if available.")


class ExecutionResult(BaseModel):
    """
    A standardized data model for the final result of an agentic orchestration.
    This ensures a consistent output format regardless of the underlying framework.
    """

    raw_output: str = Field(
        ...,
        description="The final, raw string output from the entire orchestration process.",
    )
    structured_output: Any | None = Field(
        None,
        description="The final output parsed into a structured format, if applicable.",
    )
    task_outputs: list[TaskExecutionRecord] | None = Field(
        default_factory=list,
        description="A list of outputs from each individual task executed during the run.",
    )
    metadata: dict[str, Any] | None = Field(
        default_factory=dict,
        description="A dictionary containing metadata about the execution (e.g., token usage, cost, execution time).",
    )


class AbstractTool(ABC):
    """Abstract interface for a tool that can be used by an agent."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A clear description of what the tool does and its parameters."""
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Executes the tool with the given arguments."""
        pass

    @abstractmethod
    def get_command_schemas(self) -> dict[str, type[BaseModel]] | None:
        """
        Returns a dictionary of command names to their Pydantic schemas.
        If the tool does not have commands, it returns None.
        """
        pass


class AbstractAgent(ABC):
    """Abstract definition of an agent, capturing its identity and capabilities."""

    @property
    @abstractmethod
    def role(self) -> str:
        """The specific role of the agent (e.g., 'Senior Researcher')."""
        pass

    @property
    @abstractmethod
    def goal(self) -> str:
        """The primary objective of the agent."""
        pass

    @property
    @abstractmethod
    def backstory(self) -> str:
        """A narrative background for the agent to provide context."""
        pass

    @property
    @abstractmethod
    def prompt_template(self) -> str | None:
        """Prompt template for the agent to use when interacting with the LLM."""
        pass

    @property
    @abstractmethod
    def tools(self) -> list[AbstractTool] | None:
        """A list of tools the agent is equipped with."""
        pass

    @property
    @abstractmethod
    def llm_config(self) -> dict[str, Any] | None:
        """Configuration for the language model, if specific to this agent."""
        pass

    @property
    @abstractmethod
    def llm(self) -> AbstractLLM | None:
        """The LLM instance used by the agent."""
        pass

    @property
    @abstractmethod
    def max_retries(self) -> int:
        pass

    def call_llm(self, prompt: str) -> str:
        return self.__call_llm(prompt, lambda response_text: response_text, lambda e: LLMError(e))

    def llm_json(self, prompt) -> Any:
        def llm_response_to_json(response_text: str) -> Any:
            return to_json_object(response_text)

        def llm_error_handler(e: Exception) -> LLMError:
            return LLMError(f"Failed to parse LLM response as JSON after {self.max_retries} attempts. Original error: {e}")

        return self.__call_llm(prompt, llm_response_to_json, llm_error_handler)

    def __call_llm(self, prompt: str, response_handler: Callable[[str], Any], error_handler: Callable[[Exception], Exception]) -> Any:
        """Calls the LLM and handles potential LLMError exceptions with retries."""
        base_delay = 1  # starting delay in seconds
        last_exception = None
        response_text: str | None = None
        log = structlog.get_logger()
        for attempt in range(self.max_retries):
            try:
                response_text = self.llm.call(prompt)
                return response_handler(response_text)
            except Exception as e:
                last_exception = e
                log.warning(
                    "LLM call failed, retrying...",
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    error=str(last_exception),
                    response_text=response_text,
                )
                if attempt < self.max_retries - 1:
                    delay = base_delay * (1.5**attempt)  # exponential backoff
                    time.sleep(delay)
        raise error_handler(last_exception)


class AbstractTask(ABC):
    """Abstract definition of a task to be performed by an agent."""

    @property
    @abstractmethod
    def description(self) -> str:
        """A detailed description of the task."""
        pass

    @property
    @abstractmethod
    def expected_output(self) -> str:
        """A clear description of the expected output format."""
        pass

    @property
    @abstractmethod
    def agent(self) -> AbstractAgent:
        """The agent assigned to perform this task."""
        pass

    @property
    @abstractmethod
    def dependencies(self) -> list["AbstractTask"]:
        """
        A list of other tasks that must be completed before this one can start.
        This is crucial for defining non-sequential, graph-based workflows.
        """
        pass


class AbstractOrchestrator(ABC):
    """The core abstract interface for an agent orchestrator."""

    @abstractmethod
    def __init__(self, config: dict[str, Any] | None = None):
        """Initializes the orchestrator with framework-specific configuration."""
        pass

    @abstractmethod
    def add_agent(self, agent: AbstractAgent) -> None:
        """Registers an abstract agent with the orchestrator."""
        pass

    @abstractmethod
    def add_task(self, task: AbstractTask) -> None:
        """Registers an abstract task with the orchestrator."""
        pass

    @abstractmethod
    def execute(self) -> ExecutionResult:
        """
        Executes the defined orchestration process and returns a standardized result.
        """
        pass
