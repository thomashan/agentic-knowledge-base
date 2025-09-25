from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field


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
    structured_output: Optional[Any] = Field(  # noqa: UP045
        None,
        description="The final output parsed into a structured format, if applicable.",
    )
    task_outputs: list[TaskExecutionRecord] = Field(
        default_factory=list,
        description="A list of outputs from each individual task executed during the run.",
    )
    metadata: dict[str, Any] = Field(
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
    def tools(self) -> list[AbstractTool]:
        """A list of tools the agent is equipped with."""
        pass

    @property
    @abstractmethod
    def llm_config(self) -> dict[str, Any]:
        """Configuration for the language model, if specific to this agent."""
        pass


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
    def dependencies(self) -> list["""AbstractTask"""]:
        """
        A list of other tasks that must be completed before this one can start.
        This is crucial for defining non-sequential, graph-based workflows.
        """
        pass


class AbstractOrchestrator(ABC):
    """The core abstract interface for an agent orchestrator."""

    @abstractmethod
    def __init__(self, config: dict[str, Any] = None):
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
