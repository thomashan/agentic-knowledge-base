### Implementation Plan for Orchestrator Abstraction

#### **Phase 1: Define Core Abstractions (Framework-Agnostic)**

1. **Create `AgentConfig` and `TaskConfig` in `core/`**
    - Location: `app/agents/core/config.py`
    - Purpose: Define framework-agnostic data structures for agent/task configurations.
    - Key properties:
        - `AgentConfig`: `role` (str), `goal` (str), `backstory` (str), `tools` (list of tool names/IDs), `llm_config` (dict for model params).
        - `TaskConfig`: `description` (str), `expected_output` (str), `agent` (reference to `AgentConfig`), `context` (list of task IDs).
    - *Why?* Ensures both CrewAI and LangChain use identical configuration schemas without framework dependencies.

2. **Define `AbstractOrchestrator` Interface in `core/`**
    - Location: `app/agents/core/orchestrator.py`
    - Purpose: Establish a contract for all orchestrators.
    - Abstract methods:
        - `__init__(self, agents: List[AgentConfig], tasks: List[TaskConfig])`: Initialize with configs.
        - `compile(self) -> Any`: Convert configs into framework-specific objects (returns internal framework object).
        - `run(self, inputs: Dict) -> Dict`: Execute the workflow with user inputs.
        - `validate(self) -> bool`: Check if configs are valid for the framework.
    - *Why?* Forces concrete implementations (CrewAI/LangChain) to adhere to a unified interface.

3. **Create `OrchestratorError` Base Exception**
    - Location: `app/agents/core/exceptions.py`
    - Purpose: Standardize error handling across orchestrators.
    - Subclasses: `ConfigValidationError`, `ExecutionError`, etc.
    - *Why?* Decouples error handling from framework-specific exceptions.

---

#### **Phase 2: Implement CrewAI Orchestrator (Initial Focus)**

1. **Build `CrewAIOrchestrator` in `orchestrator/crewai/`**
    - Location: `app/agents/orchestrator/crewai/crewai_orchestrator.py`
    - Implementation:
        - Inherit from `core.AbstractOrchestrator`.
        - **`compile()`**:
            - Convert `AgentConfig` → CrewAI `Agent` (using `AgentConfig` properties).
            - Convert `TaskConfig` → CrewAI `Task` (resolve agent references via `AgentConfig.role`).
            - Return CrewAI `Crew` object.
        - **`run(inputs)`**:
            - Call `Crew.kickoff(inputs)` and return structured output.
            - Handle CrewAI-specific errors (e.g., `TaskError`) → raise `core.ExecutionError`.
        - **`validate()`**:
            - Check for CrewAI-specific constraints (e.g., no duplicate agent roles).

2. **Add CrewAI-Specific Utilities**
    - Location: `app/agents/orchestrator/crewai/utils.py`
    - Purpose: Isolate CrewAI translation logic.
    - Functions:
        - `config_to_crewai_agent(config: AgentConfig) -> Agent`
        - `config_to_crewai_task(config: TaskConfig, agents: Dict[str, Agent]) -> Task`
    - *Why?* Keeps `crewai_orchestrator.py` focused on orchestration flow, not translation details.

---

#### **Phase 3: Prepare for Future LangChain Support**

1. **Stub LangChain Implementation**
    - Location: `app/agents/orchestrator/langchain/langchain_orchestrator.py`
    - Implementation:
        - Inherit from `core.AbstractOrchestrator`.
        - All methods raise `NotImplementedError` with clear message:  
          `"LangChain orchestrator not implemented yet. Use 'crewai' for now."`
    - *Why?* Maintains structural parity with CrewAI and avoids runtime errors if accidentally selected.

2. **LangChain Interface Blueprint**
    - Location: `app/agents/orchestrator/langchain/README.md`
    - Content:
        - Checklist of LangChain components needed (e.g., `AgentExecutor`, `Tool` mappings).
        - Notes on differences vs. CrewAI (e.g., task sequencing vs. agent delegation).
    - *Why?* Documents requirements for future LangChain implementation without blocking CrewAI work.

---

#### **Phase 4: Orchestrator Factory & Configuration**

1. **Create Orchestrator Factory**
    - Location: `app/agents/orchestrator/factory.py`
    - Purpose: Instantiate the correct orchestrator based on runtime config.
    - Function:
      ```python
      def create_orchestrator(
          framework: str, 
          agents: List[AgentConfig], 
          tasks: List[TaskConfig]
      ) -> AbstractOrchestrator:
          if framework == "crewai":
              from .crewai import CrewAIOrchestrator
              return CrewAIOrchestrator(agents, tasks)
          elif framework == "langchain":
              from .langchain import LangChainOrchestrator
              return LangChainOrchestrator(agents, tasks)
          else:
              raise ValueError(f"Unsupported framework: {framework}")
      ```
    - *Why?* Centralizes orchestrator selection logic; no framework leaks into app core.

2. **Add Configuration Validation**
    - Location: `app/agents/orchestrator/validator.py`
    - Purpose: Validate configs *before* passing to orchestrators.
    - Checks:
        - All task `agent` references exist in `agents`.
        - No circular dependencies in `TaskConfig.context`.
    - *Why?* Catches config errors early, regardless of orchestrator.

---

#### **Phase 5: Integration & Safety Nets**

1. **Update `orchestrator/__init__.py`**
    - Expose only the factory and core interfaces:
      ```python
      from .factory import create_orchestrator
      from .validator import validate_configs
      from ..core.orchestrator import AbstractOrchestrator
      ```
    - *Why?* Prevents direct imports of framework-specific code (e.g., `crewai_orchestrator`).

2. **Add Framework-Agnostic Output Schema**
    - Location: `app/agents/core/output.py`
    - Purpose: Standardize orchestrator output structure.
    - Class:
      ```python
      class OrchestratorOutput:
          final_result: str
          task_results: Dict[str, str]  # task_id → output
          execution_time: float
      ```
    - *Why?* Ensures consistent output parsing downstream, regardless of framework.

3. **Implement Logging Abstraction**
    - Location: `app/agents/core/logging.py`
    - Purpose: Decouple logging from framework internals.
    - Interface:
      ```python
      class OrchestratorLogger:
          def log_task_start(self, task_id: str): ...
          def log_task_result(self, task_id: str, result: str): ...
      ```
    - *Why?* Allows injecting custom loggers (e.g., for observability) without modifying orchestrators.

---

### Key Abstraction Principles Applied

1. **Separation of Concerns**
    - `core/`: Pure abstractions (no framework code).
    - `orchestrator/{framework}/`: Framework-specific *implementations only*.

2. **Config-Driven Design**
    - All orchestrators consume `AgentConfig`/`TaskConfig` → no hardcoding of framework objects in app logic.

3. **Forward Compatibility**
    - LangChain stubs and blueprints ensure zero rework when adding support later.

4. **Validation at Boundaries**
    - Config validation happens *before* orchestrator initialization → fails fast.

5. **Output Standardization**
    - Orchestrator output is normalized → app core never handles framework-specific objects.

### Next Steps After This Plan

1. Implement `core/` abstractions (Phase 1).
2. Build CrewAI orchestrator (Phase 2) with unit tests.
3. Integrate factory into app entrypoint (e.g., `main.py` selects orchestrator via env var).
4. *Later*: Replace LangChain stubs with real implementation using the same `core` interfaces.
