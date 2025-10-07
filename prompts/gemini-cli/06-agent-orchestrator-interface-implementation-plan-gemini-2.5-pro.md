# Consolidated Plan: Framework-Agnostic Agent Orchestrator

## 1. Overview & Architectural Principles

### 1.1. Strategic Goal

The primary objective is to architect a stable, internal core of abstract interfaces that decouples the application's business logic from the concrete implementation details of any single agent orchestration framework (
e.g., CrewAI, LangChain). This mitigates the risk of framework lock-in, ensuring architectural longevity and flexibility in a rapidly evolving AI landscape.

### 1.2. Architectural Approach: The Adapter Pattern

The architecture will be formally modeled on the **Adapter Pattern**.

- **`app/agents-core/`**: This package contains the **target interfaces**—a set of Abstract Base Classes (ABCs) and Pydantic models that define the system's internal, framework-agnostic representation of agents,
  tasks, and orchestration. All core abstractions are currently defined in `src/agents_core/core.py`.
- **`app/agents-orchestrator-*/`**: These packages house the **Adapters**. Each package (e.g., `agents-orchestrator-crewai/`, `agents-orchestrator-langchain/`) contains a concrete implementation of the core orchestrator interface, responsible for
  translating the system's abstract concepts into the specific API calls of the target framework.

The application's business logic will interact exclusively with the core interfaces. The core interface will delegate calls to the configured adapter, which manages the underlying framework's components.

### 1.3. Core Design Principles

- **Framework Agnosticism**: The core system must remain entirely unaware of the specific orchestration framework being used.
- **Modularity & Extensibility**: Adding support for a new framework should be a self-contained task of creating a new adapter, requiring no changes to the core.
- **Testability**: The abstraction layer allows for the creation of a `MockOrchestrator` for fast, reliable, and inexpensive unit and integration tests.
- **Configuration-Driven**: The selection and parameterization of the orchestrator and its underlying components (like LLMs) must be managed through external configuration, not hardcoded.

## 2. Proposed Directory Structure

This structure reflects the current project layout, with each component as a separate package.

```
app/
├── agents-core/
│   ├── pyproject.toml
│   └── src/
│       └── agents_core/
│           ├── __init__.py
│           └── core.py         # Contains all core abstractions (ABC, Models, Exceptions)
│
├── agents-orchestrator-factory/
│   ├── pyproject.toml
│   └── src/
│       └── factory/
│           ├── __init__.py
│           └── factory.py      # OrchestratorFactory for creating instances
│
├── agents-orchestrator-crewai/
│   ├── pyproject.toml
│   └── src/
│       └── crewai_adapter/
│           ├── __init__.py
│           └── adapter.py      # Concrete implementation for CrewAI
│
└── agents-orchestrator-langchain/
    ├── pyproject.toml
    └── src/
        └── langchain_adapter/
            ├── __init__.py
            └── adapter.py      # Skeleton for future LangChain implementation
```

## 3. Core Abstractions (from `app/agents-core/`)

This is the definitive contract for all components interacting with the orchestration layer.

### 3.1. Data Models (in `core.py`)

Using Pydantic ensures robust data validation and serialization.

```
# Excerpt from app/agents-core/src/agents_core/core.py

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TaskExecutionRecord(BaseModel):
    """A record of the output from a single task execution."""
    task_description: str = Field(..., description="The original description of the task.")
    raw_output: str = Field(..., description="The raw string output of the task.")
    structured_output: Optional[Any] = Field(None, description="Structured output, if available.")

class ExecutionResult(BaseModel):
    """
    A standardized data model for the final result of an agentic orchestration.
    This ensures a consistent output format regardless of the underlying framework.
    """
    raw_output: str = Field(..., description="The final, raw string output from the entire orchestration process.")
    structured_output: Optional[Any] = Field(None, description="The final output parsed into a structured format, if applicable.")
    task_outputs: List[TaskExecutionRecord] = Field(default_factory=list, description="A list of outputs from each individual task executed during the run.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="A dictionary containing metadata about the execution (e.g., token usage, cost, execution time).")

```

### 3.2. Core Contracts (in `core.py`)

These ABCs define the essential components of the agentic system.

```
# Excerpt of ABCs from app/agents-core/src/agents_core/core.py

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
    def dependencies(self) -> Optional[List['AbstractTask']]:
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
```

## 4. Initial Implementation: The CrewAI Adapter

The `CrewAIOrchestrator` will be the first concrete implementation of `AbstractOrchestrator`.

### Responsibilities:

1. **Initialization**: The `__init__` method will accept a configuration dictionary and parse CrewAI-specific settings (e.g., `process`, `manager_llm`, `memory`). It will also initialize internal lists to hold translated
   `crewai.Agent` and `crewai.Task` objects.
2. **Translation**:
    - `add_agent`: This method will receive an `AbstractAgent` and instantiate a corresponding `crewai.Agent`, mapping the properties (`role`, `goal`, `backstory`, `tools`) directly. The concrete `crewai.Agent` is stored
      internally.
    - `add_task`: This method will receive an `AbstractTask` and instantiate a `crewai.Task`, mapping `description` and `expected_output`. It will look up the corresponding `crewai.Agent` from its internal list to assign
      the task correctly.
3. **Execution**:
    - The `execute` method will instantiate a `crewai.Crew`, passing the internally stored lists of concrete agents and tasks, along with the parsed configuration.
    - It will call `crew.kickoff()` to run the workflow.
    - **Crucially**, it will then translate the returned `CrewOutput` object into the system's standardized `ExecutionResult` data model, ensuring the abstraction boundary is maintained.

## 5. Phased Implementation Roadmap

- **Phase 1: Core Foundation (1-2 Sprints)**
    1. Implement all Pydantic data models in `app/agents-core/src/agents_core/core.py`.
    2. Define all Abstract Base Classes (ABCs) in `app/agents-core/src/agents_core/core.py`.
    3. Define the custom exception hierarchy in `app/agents-core/src/agents_core/core.py`.
    4. Develop unit tests for the core components using a mock orchestrator.

- **Phase 2: CrewAI Integration (2-3 Sprints)**
    1. Implement the `CrewAIOrchestrator` adapter in `app/agents-orchestrator-crewai/src/crewai_adapter/adapter.py`.
    2. Implement the `OrchestratorFactory` in `app/agents-orchestrator-factory/src/factory/factory.py`.
    3. Develop integration tests for the adapter, using a mock or inexpensive LLM.
    4. Write documentation on configuring and using the `CrewAIOrchestrator`.

- **Phase 3: Demonstration & Refinement (1 Sprint)**
    1. Build a proof-of-concept application that uses the system to solve a concrete problem (e.g., a research-and-summarize workflow).
    2. Create the skeleton for the `LangChainOrchestrator` to validate the abstraction.
    3. Refine the core interfaces based on the experience of building the PoC.

## 6. Strategic Recommendations

- **Dependency Injection for LLMs**: The orchestrator configuration should be the single source of truth for LLM selection. The adapter should be responsible for dynamically instantiating the correct LLM client (e.g.,
  from `langchain_openai`, `langchain_google_genai`) based on this configuration.
- **Centralized Configuration**: Use a library like Pydantic's `BaseSettings` to manage all system-wide settings (API keys, orchestrator choice, logging levels) from environment variables or a `.env` file.
- **Abstracted Observability**: Enhance the `AbstractOrchestrator` to accept a standardized `Tracer` or `Logger` object. The concrete adapter will be responsible for wiring up the underlying framework's native
  callbacks (e.g., CrewAI's `step_callback`) to this object, providing a single, unified view for monitoring and debugging.
