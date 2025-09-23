Of course. Here is a detailed implementation plan for building an abstracted agentic orchestration layer, focusing on `crewai` as the initial implementation while ensuring future compatibility with `langchain`.

### Project Goal

The primary goal is to create a modular, framework-agnostic orchestration system. The core application logic should interact with a generic `Orchestrator` interface, which can be backed by different agentic frameworks (
`crewai`, `langchain`, etc.) without requiring changes to the business logic.

-----

### Phase 1: Core Abstract Components

This phase focuses on defining the framework-agnostic data models and interfaces in the `app/agents/core/` directory. These classes will represent the fundamental concepts of an agentic workflow, independent of any
specific library.

1. **File:** `app/agents/core/entities.py`

    * **Purpose:** To define the core data structures for agents and tasks using Pydantic for data validation and structure.
    * **Plan:**
        * Create a `Tool` class (or alias `typing.Callable`) to represent a function that an agent can use.
        * Create a Pydantic model named `AgentConfig`.
            * **Fields:** `role: str`, `goal: str`, `backstory: str`, `tools: list[Tool]`, `allow_delegation: bool = False`, `verbose: bool = True`.
            * **Rationale:** This captures the essential attributes of any agent, regardless of the framework.
        * Create a Pydantic model named `TaskConfig`.
            * **Fields:** `name: str`, `description: str`, `expected_output: str`, `agent_config: AgentConfig`.
            * **Rationale:** This defines a unit of work and explicitly links it to the agent responsible for it.

2. **File:** `app/agents/core/orchestrator.py`

    * **Purpose:** To define the abstract base class (ABC) for all orchestrators. This interface is the single most important contract in the design.
    * **Plan:**
        * Create an abstract class `AbstractOrchestrator`.
        * Define an `__init__` method that can accept configuration if needed.
        * Define an abstract method: `run(tasks: list[TaskConfig]) -> str`.
            * **Parameters:** It will take a list of `TaskConfig` objects, which contains all the necessary information (task descriptions and their assigned agents).
            * **Returns:** A string representing the final result of the orchestration.
            * **Rationale:** This method provides a simple, unified entry point to execute a workflow. The complexity of how agents and tasks are assembled and run is hidden within the concrete implementations.

-----

### Phase 2: CrewAI Concrete Implementation

This phase involves implementing the `AbstractOrchestrator` interface specifically for the `crewai` framework. All work here will be inside the `app/agents/orchestrator/crewai/` directory.

1. **File:** `app/agents/orchestrator/crewai/mapper.py`

    * **Purpose:** To create helper functions that convert our abstract `AgentConfig` and `TaskConfig` models into `crewai`'s native `Agent` and `Task` objects.
    * **Plan:**
        * Create a function `map_agent(config: AgentConfig) -> crewai.Agent`.
            * This function will instantiate a `crewai.Agent` object using the fields from our `AgentConfig` Pydantic model.
        * Create a function `map_task(config: TaskConfig, agent_map: dict[str, crewai.Agent]) -> crewai.Task`.
            * This function will instantiate a `crewai.Task` object.
            * It will use the `agent_map` dictionary to look up the corresponding `crewai.Agent` instance for the task based on the agent's role or a unique identifier.

2. **File:** `app/agents/orchestrator/crewai/orchestrator.py`

    * **Purpose:** To create the concrete implementation of `AbstractOrchestrator` for `crewai`.
    * **Plan:**
        * Create a class `CrewAIOrchestrator` that inherits from `AbstractOrchestrator`.
        * Implement the `run(tasks: list[TaskConfig]) -> str` method.
            * **Step 1: Agent Instantiation.** Iterate through the unique `AgentConfig` objects from the list of tasks. For each `AgentConfig`, call the `map_agent` helper to create a `crewai.Agent` instance. Store these
              in a dictionary mapping the agent's role to the instance (this will be our `agent_map`).
            * **Step 2: Task Instantiation.** Iterate through the `TaskConfig` list. For each one, call the `map_task` helper, passing the config and the `agent_map`, to create a `crewai.Task` instance. Collect these in
              a list.
            * **Step 3: Crew Creation.** Instantiate `crewai.Crew` with the created lists of agents and tasks. We can configure the process here (e.g., `Process.sequential`). This can be hardcoded for now or passed in
              via the orchestrator's `__init__`.
            * **Step 4: Execution.** Call the `crew.kickoff()` method.
            * **Step 5: Return Result.** Return the output from `kickoff()`.

-----

### Phase 3: Wiring and Usage (Conceptual)

This section describes how the system would be used in practice, demonstrating the value of the abstraction.

1. **Application Logic (e.g., in a service layer file, not shown in the diagram):**
    * The application would first define the agents and tasks it needs using the framework-agnostic `AgentConfig` and `TaskConfig` models.
    * It would then decide which orchestrator to use.
    * **Example:**
      ```
      # 1. Define configurations
      researcher_config = AgentConfig(role="Researcher", ...)
      writer_config = AgentConfig(role="Writer", ...)

      research_task_config = TaskConfig(name="Research", ..., agent_config=researcher_config)
      write_task_config = TaskConfig(name="Write", ..., agent_config=writer_config)

      all_tasks = [research_task_config, write_task_config]

      # 2. Instantiate the desired orchestrator
      orchestrator: AbstractOrchestrator = CrewAIOrchestrator()

      # 3. Run the process
      result = orchestrator.run(all_tasks)
      ```
    * **Benefit:** To switch to a future LangChain implementation, only the instantiation line would need to change: `orchestrator = LangChainOrchestrator()`. The definitions of agents and tasks would remain untouched.

-----

### Future-Proofing: Plan for LangChain

This section outlines how the `langchain` implementation would fit into the existing structure, validating the design.

1. **Directory:** `app/agents/orchestrator/langchain/`
    * **Plan:**
        * A `mapper.py` file would be created here to map `AgentConfig` and `TaskConfig` to LangChain's graph nodes or agent runnables.
        * An `orchestrator.py` file would define `LangChainOrchestrator(AbstractOrchestrator)`.
        * The `run` method in this class would be responsible for constructing a `LangGraph` or `LCEL` chain using the provided configurations and executing it.

By following this plan, you will build a clean, decoupled system where the core logic is completely isolated from the specifics of the underlying agentic framework. This makes the system more maintainable, testable, and
adaptable to future changes in the AI landscape.
