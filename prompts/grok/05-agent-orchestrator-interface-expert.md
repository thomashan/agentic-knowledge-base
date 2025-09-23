### Implementation Plan

To implement the orchestrator logic with sufficient abstraction to support both CrewAI and LangChain frameworks, while starting with CrewAI as the initial implementation, we'll follow a structured approach. The goal is
to keep framework-agnostic logic (e.g., interfaces and shared utilities) in `app/agents/core/`, and place framework-specific orchestrator implementations in `app/agents/orchestrator/crewai/` and
`app/agents/orchestrator/langchain/`. This ensures modularity, allowing easy switching or extension between frameworks without altering core business logic.

The plan focuses on the orchestrator and its abstractions, avoiding any agent-specific details (e.g., no individual agent classes or behaviors in `app/agents/`). We'll define minimal ABCs to capture the essence of
orchestration: initializing the system, configuring tasks/workflows, executing them, and handling outputs. This abstraction level is "enough" to support both frameworks, as CrewAI emphasizes crew-based task
orchestration, while LangChain focuses on chain/reactor-style workflows— the ABCs will bridge these by defining common entry points.

#### Step-by-Step Implementation Plan

1. **Set Up Directory Structure Refinements**:
    - Ensure `app/agents/core/` has files for ABCs and any shared utilities (e.g., add `orchestrator.py` for ABC definitions).
    - In `app/agents/orchestrator/`, add a top-level `__init__.py` for importing and a factory function to select implementations.
    - In `app/agents/orchestrator/crewai/`, add `orchestrator.py` for the CrewAI-specific class.
    - In `app/agents/orchestrator/langchain/`, add `orchestrator.py` as a stub (for future implementation), inheriting from the ABC.

2. **Define Abstract Base Classes (ABCs) in `app/agents/core/`**:
    - Create `AbstractOrchestrator` as the primary ABC, defining framework-agnostic methods for orchestration lifecycle (e.g., init, configure, run).
    - If needed, add supporting ABCs like `AbstractTask` for task definitions (kept minimal and agnostic, focusing on inputs/outputs rather than agent internals).
    - Include docstrings for each ABC and method to document purpose, parameters, and expected behavior.
    - Add any shared utilities (e.g., error handling or config parsing) in a separate file like `utils.py`.

3. **Implement CrewAI-Specific Orchestrator**:
    - In `app/agents/orchestrator/crewai/orchestrator.py`, create `CrewAIOrchestrator` inheriting from `AbstractOrchestrator`.
    - Map ABC methods to CrewAI concepts: e.g., `configure` sets up crews/tasks, `run` kicks off the crew.
    - Use CrewAI libraries (assume installed via project dependencies) for internal logic.
    - Handle CrewAI-specific configurations (e.g., agent lists, task sequences) but keep them encapsulated.

4. **Stub LangChain-Specific Orchestrator**:
    - In `app/agents/orchestrator/langchain/orchestrator.py`, create `LangChainOrchestrator` inheriting from `AbstractOrchestrator`.
    - Implement stubs (e.g., raise NotImplementedError) for methods, to be filled in later.
    - Ensure it aligns with LangChain's chain-based orchestration (e.g., `run` might invoke a chain or agent executor).

5. **Add Factory and Entry Points in `app/agents/orchestrator/__init__.py`**:
    - Create a factory function (e.g., `get_orchestrator(framework: str) -> AbstractOrchestrator`) that returns the appropriate implementation (default to 'crewai').
    - This allows higher-level app code to use the orchestrator without knowing the framework.

6. **Testing and Integration**:
    - Write unit tests for the ABCs (e.g., ensure subclasses implement all abstract methods).
    - Integrate with the broader app by importing the factory in higher-level modules.
    - Initially test with CrewAI: mock tasks/configs and verify execution.
    - Ensure extensibility: adding LangChain support should only require filling in the stubs without changing core or other implementations.

7. **Documentation and Best Practices**:
    - Add inline comments and docstrings throughout.
    - Follow Python best practices: type hints, PEP8, and dependency injection for configs.
    - Version control: Commit ABCs first, then CrewAI impl, then stubs.

This plan ensures the system is framework-agnostic at the core, with initial focus on CrewAI, and scalable for LangChain.

### ABC Definitions and Documentation

Below are the proposed ABC definitions for the core and orchestrator-agnostic interfaces. These will be placed in `app/agents/core/orchestrator.py`. I've included full code snippets with docstrings for clarity. The
abstractions are kept lightweight: `AbstractOrchestrator` handles the main lifecycle, and `AbstractTask` provides a simple task interface (agnostic to frameworks, focusing on inputs/outputs for orchestration).

```
# app/agents/core/orchestrator.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AbstractTask(ABC):
    """
    Abstract base class for defining tasks in an agnostic way.
    This represents a unit of work that can be orchestrated, without tying to specific
    framework implementations (e.g., CrewAI Task or LangChain Chain).
    
    Attributes:
        description (str): A human-readable description of the task.
        inputs (Dict[str, Any]): Input data required for the task.
        expected_output (str): Description of the expected output format.
    
    This ABC ensures tasks can be passed to orchestrators uniformly, allowing frameworks
    to map them to their native constructs during configuration.
    """

    def __init__(self, description: str, inputs: Optional[Dict[str, Any]] = None, expected_output: str = ""):
        """
        Initializes the abstract task.
        
        Args:
            description (str): Description of what the task does.
            inputs (Optional[Dict[str, Any]]): Key-value pairs of input data.
            expected_output (str): Expected output format or type description.
        """
        self.description = description
        self.inputs = inputs or {}
        self.expected_output = expected_output

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the task to a dictionary representation for serialization or framework mapping.
        
        Returns:
            Dict[str, Any]: Dictionary of task attributes.
        """
        pass


class AbstractOrchestrator(ABC):
    """
    Abstract base class for orchestrators, providing a framework-agnostic interface
    for managing and executing workflows of tasks.
    
    This ABC defines the core lifecycle methods for orchestration:
    - Initialization with configuration.
    - Configuration of tasks/workflows.
    - Execution of the orchestrated process.
    - Retrieval of results.
    
    Subclasses (e.g., for CrewAI or LangChain) must implement these methods to map
    to their specific framework's APIs, ensuring the higher-level app logic remains unchanged
    when switching frameworks.
    
    Attributes:
        config (Dict[str, Any]): Configuration settings (e.g., API keys, model params).
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the orchestrator with configuration.
        
        Args:
            config (Dict[str, Any]): Framework-agnostic config (e.g., {'llm_model': 'gpt-4', 'max_retries': 3}).
        """
        self.config = config

    @abstractmethod
    def configure(self, tasks: List[AbstractTask]) -> None:
        """
        Configures the orchestrator with a list of tasks, setting up the workflow.
        This method should map abstract tasks to framework-specific constructs (e.g., CrewAI crews or LangChain chains).
        
        Args:
            tasks (List[AbstractTask]): List of tasks to orchestrate.
        
        Raises:
            ValueError: If tasks are invalid or configuration fails.
        """
        pass

    @abstractmethod
    def run(self, initial_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the configured workflow and returns the results.
        
        Args:
            initial_input (Optional[Dict[str, Any]]): Optional starting inputs for the orchestration.
        
        Returns:
            Dict[str, Any]: Results of the execution (e.g., {'output': ..., 'logs': ...}).
        
        Raises:
            RuntimeError: If execution fails.
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Retrieves the current status of the orchestrator (e.g., 'idle', 'running', 'completed').
        
        Returns:
            str: Status string.
        """
        pass
```
