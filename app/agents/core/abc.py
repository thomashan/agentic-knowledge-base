# app/agents/core/abc.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .models import ExecutionResult


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
    def tools(self) -> List[AbstractTool]:
        """A list of tools the agent is equipped with."""
        pass

    @property
    @abstractmethod
    def llm_config(self) -> Optional[Dict[str, Any]]:
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
    def dependencies(self) -> Optional[List['''AbstractTask''']]:
        """
        A list of other tasks that must be completed before this one can start.
        This is crucial for defining non-sequential, graph-based workflows.
        """
        pass


class AbstractOrchestrator(ABC):
    """The core abstract interface for an agent orchestrator."""

    @abstractmethod
    def __init__(self, config: Optional[Dict[str, Any]] = None):
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
