### Implementation Plan for Orchestrator Logic

#### 1. Overview and Goals

The orchestrator will serve as the central coordinator for the agentic knowledge base system, responsible for managing workflows, task delegation, and collaboration among various agents (e.g., planner, research,
retrieval, knowledge, intelligence). It will handle the sequencing of tasks, monitoring progress, and aggregating results to achieve high-level goals like querying, updating, or expanding the knowledge base.

Key goals:

- **Abstraction for Flexibility**: Place framework-agnostic logic in `app/agents/core/` to define interfaces and shared utilities that can be implemented by different orchestration frameworks (initially CrewAI, with
  extensibility for LangChain).
- **Framework-Specific Implementations**: Put CrewAI-specific logic in `app/agents/orchestrator/crewai/` and prepare a skeleton for LangChain in `app/agents/orchestrator/langchain/`.
- **Initial Focus on CrewAI**: Fully flesh out the CrewAI implementation first, ensuring it integrates seamlessly with the abstractions. LangChain support will be stubbed out initially (e.g., with abstract methods or
  placeholders) to allow future extension without refactoring the core.
- **No Agent-Specific Logic**: Avoid detailing implementations for individual agents (e.g., planner or research) in this plan. Assume they will expose standardized interfaces that the orchestrator can interact with.
- **Modularity and Extensibility**: Use design patterns like factories, interfaces, and dependency injection to allow switching between orchestrators (e.g., via configuration) without affecting the rest of the system.
- **Testing and Iteration**: Plan for unit/integration tests for abstractions and CrewAI implementation, with placeholders for LangChain tests.

The plan assumes Python as the language, leveraging object-oriented principles for abstraction.

#### 2. Define Abstractions in `app/agents/core/`

This directory will contain framework-agnostic classes, interfaces, and utilities that define the "what" without the "how" (i.e., no dependencies on CrewAI or LangChain). Use abstract base classes (ABCs) from `abc`
module to enforce contracts.

- **Orchestrator Interface**:
    - Create an abstract class `AbstractOrchestrator` that defines the core methods for orchestration:
        - `initialize(workflow_config: Dict)`: Sets up the orchestrator with a configuration (e.g., agent roles, task sequences, goals).
        - `run(goal: str, inputs: Dict) -> Dict`: Executes the workflow for a given goal (e.g., "query knowledge base") with inputs, returning aggregated results.
        - `monitor_progress() -> Dict`: Provides status updates on ongoing tasks (e.g., completion percentage, errors).
        - `handle_error(error: Exception) -> None`: Abstract error handling logic.
        - `add_task(task: AbstractTask)`: Dynamically adds tasks to the workflow.
    - This interface ensures any concrete orchestrator (CrewAI or LangChain) implements these methods uniformly.

- **Task Abstraction**:
    - Define `AbstractTask` as an ABC representing a unit of work:
        - Attributes: `description: str`, `expected_output: str`, `dependencies: List[AbstractTask]`.
        - Methods: `execute(context: Dict) -> Dict` (runs the task with shared context), `validate_output(output: Dict) -> bool`.
    - This allows tasks to be defined agnostically, with framework-specific wrappers handling execution.

- **Agent Role Abstraction**:
    - Create `AbstractAgentRole` to represent roles (e.g., "planner", "researcher") without tying to specific agents:
        - Attributes: `role_name: str`, `capabilities: List[str]` (e.g., ["search", "analyze"]).
        - Methods: `assign_task(task: AbstractTask) -> None`.
    - This decouples agent definitions from orchestration, allowing the orchestrator to assign tasks to roles.

- **Workflow Configuration**:
    - Define a `WorkflowConfig` dataclass or pydantic model for declarative workflows:
        - Fields: `goals: List[str]`, `tasks: List[AbstractTask]`, `agent_roles: List[AbstractAgentRole]`, `sequence: List[Tuple[str, str]]` (e.g., task-to-agent mappings).
    - This enables loading workflows from YAML/JSON files, keeping them framework-agnostic.

- **Shared Utilities**:
    - Add utility functions/classes:
        - `ContextManager`: A class to handle shared state across tasks (e.g., a dict for passing data like query results).
        - `LoggerMixin`: A mixin for standardized logging across orchestrators.
        - `Validator`: Functions to validate configs, tasks, and outputs (e.g., schema checks).

- **Factory Pattern for Instantiation**:
    - Implement a `OrchestratorFactory` class with a static method `create(orchestrator_type: str, config: WorkflowConfig) -> AbstractOrchestrator`.
        - Supports "crewai" and "langchain" as types; raises NotImplementedError for unsupported types.
        - This factory will be the entry point for the system to instantiate the appropriate orchestrator.

No framework imports here—keep it pure Python.

#### 3. CrewAI-Specific Implementation in `app/agents/orchestrator/crewai/`

Build concrete classes that inherit from the core abstractions, integrating CrewAI's concepts (e.g., Crew, Agent, Task). Depend on the `crewai` library here.

- **Concrete Orchestrator**:
    - Create `CrewAIOrchestrator` subclassing `AbstractOrchestrator`.
        - In `initialize`, map abstract tasks and roles to CrewAI's `Task` and `Agent` objects, then build a `Crew` instance.
        - In `run`, kick off the Crew's execution (e.g., `crew.kickoff()`), passing inputs and collecting outputs.
        - Implement `monitor_progress` using CrewAI's process monitoring if available, or simulate via callbacks.
        - For `handle_error`, wrap CrewAI exceptions and retry logic.
        - Use CrewAI's sequential or hierarchical process modes based on workflow config.

- **Task and Role Wrappers**:
    - `CrewAITask` subclassing `AbstractTask`: Wraps CrewAI's `Task`, translating abstract attributes to CrewAI-specific ones (e.g., `tools`, `agent`).
    - `CrewAIAgentRole` subclassing `AbstractAgentRole`: Maps to CrewAI's `Agent`, configuring backstory, goals, and tools.

- **Integration Helpers**:
    - Add a `CrewAIBuilder` class to construct the Crew from the abstract config:
        - Steps: Iterate over abstract tasks/roles, create wrappers, assemble into a Crew.
    - Handle CrewAI-specific configs (e.g., verbose mode, memory) via extensions to the abstract WorkflowConfig.

- **Initial Setup**:
    - In `__init__.py`, export `CrewAIOrchestrator` and register it with the factory (e.g., via a registry dict).
    - Assume initial workflows will be simple sequences (e.g., plan -> research -> retrieve -> synthesize), testable with mock agents.

Focus on making this implementation complete and testable standalone, using the abstractions.

#### 4. LangChain Preparation in `app/agents/orchestrator/langchain/`

To support future extension, create skeletal implementations that mirror CrewAI's structure but raise NotImplementedError where appropriate. This ensures the abstraction layer can be tested for compatibility.

- **Concrete Orchestrator Stub**:
    - Create `LangChainOrchestrator` subclassing `AbstractOrchestrator`.
        - For each method (e.g., `run`), implement a stub that raises NotImplementedError with a message like "LangChain support pending implementation."
        - Add comments outlining planned mapping: e.g., abstract tasks to LangChain's `Runnable` or `Chain`, roles to `AgentExecutor`.

- **Task and Role Stubs**:
    - `LangChainTask` and `LangChainAgentRole` subclassing the abstracts, with stubbed methods.
    - Include a `LangChainBuilder` stub similar to CrewAI's.

- **Placeholder Setup**:
    - In `__init__.py`, export the stubs and register with the factory.
    - Plan for future: When implementing, leverage LangChain's LCEL (LangChain Expression Language) for chaining, ensuring the same abstract methods are fulfilled.

This keeps the directory ready without blocking the initial CrewAI rollout.

#### 5. Integration and Usage

- **Entry Point**: The system will use `OrchestratorFactory.create("crewai", config)` to get an instance, then call `orchestrator.run(goal, inputs)`.
- **Configuration Loading**: Load workflows from external files (e.g., YAML in a configs/ dir), parsing into `WorkflowConfig`.
- **Dependency Management**: Ensure `crewai` is a dependency in requirements.txt; `langchain` as optional/extra.
- **Extensibility Hooks**: In core/, add extension points like callbacks for custom behavior in run/monitor methods.
- **Error Handling and Logging**: Standardize across implementations using the LoggerMixin.
- **Testing Strategy**:
    - Unit tests for core abstractions (e.g., mock implementations).
    - Integration tests for CrewAI (using mock agents/tasks).
    - Future: Add LangChain tests once implemented.
- **Iteration Plan**:
    - Phase 1: Implement core abstractions.
    - Phase 2: Build and test CrewAI implementation.
    - Phase 3: Add LangChain stubs and validate factory switching.
    - Phase 4: Integrate with other agents (e.g., via role assignments), assuming they implement compatible interfaces.

This plan ensures a modular, extensible orchestrator starting with CrewAI, while preparing for LangChain without over-engineering.
