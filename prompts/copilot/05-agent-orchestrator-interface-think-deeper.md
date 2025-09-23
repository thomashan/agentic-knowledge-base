### Overview

Clear separation: framework-agnostic domain logic in app/agents/core and orchestrator implementations in app/agents/orchestrator. Build abstract interfaces (ABCs) that both crewai and langchain orchestrators implement.
Implement crewai first.

---

### Goals

- Define minimal, expressive core abstractions for orchestrating agent workflows, state, actions, and events.
- Provide orchestrator interfaces that adapt core abstractions to a concrete framework.
- Keep core free of any crewai or langchain imports so it can be reused or tested independently.
- Deliver a working crewai orchestrator implementation and tests that exercise the core contracts.

---

### High-level implementation plan

1. Create core API surface (ABCs + data types) under app/agents/core:
    - Value objects: Task, Action, Result, AgentConfig, OrchestrationContext.
    - ABCs: AgentInterface, OrchestratorInterface, ActionExecutor, StateStore, EventBus.
    - Utilities: serialization, validation, type hints.

2. Create orchestrator adapter layer under app/agents/orchestrator:
    - Shared orchestrator base common to crewai/langchain (framework-agnostic orchestrator glue).
    - crewai adapter implementing OrchestratorInterface and AgentInterface using crewai SDK primitives.
    - langchain adapter stub skeleton implementing same interfaces (for later).

3. Implement integration tests that instantiate core contracts with the crewai implementation:
    - Unit tests for each ABC contract using fake/stub implementations.
    - End-to-end test: simple Agent config + crewai orchestrator running a scripted action.

4. Add docs and docstrings for all core ABCs and orchestrator interfaces in code and a README at app/agents/core/README.md and app/agents/orchestrator/README.md.

5. CI: run lint, type-checking (mypy), tests.

6. Iterate: expand interfaces as new needs appear.

Estimate: MVP in 1–2 weeks depending on developer familiarity with crewai.

---

### Directory layout proposal

- app/agents/core/
    - __init__.py
    - models.py
    - interfaces.py
    - exceptions.py
    - utils.py
    - README.md
    - tests/
- app/agents/orchestrator/
    - __init__.py
    - base.py
    - crewai/
        - __init__.py
        - orchestrator.py
        - agent_adapter.py
        - tests/
    - langchain/
        - __init__.py
        - orchestrator.py (skeleton)
        - tests/

---

### Core ABCs and minimal data models

Files: app/agents/core/models.py and app/agents/core/interfaces.py

Example models.py

```
from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class Task:
    id: str
    prompt: str
    metadata: Mapping[str, Any] = None


@dataclass(frozen=True)
class Action:
    name: str
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class Result:
    success: bool
    output: Any = None
    error: Optional[str] = None


@dataclass(frozen=True)
class AgentConfig:
    agent_id: str
    default_timeout_seconds: int = 60


@dataclass
class OrchestrationContext:
    task: Task
    agent_config: AgentConfig
    state: Mapping[str, Any]
```

Example interfaces.py

```
from abc import ABC, abstractmethod
from typing import Iterable, Protocol, Any
from .models import Task, Action, Result, AgentConfig, OrchestrationContext


class ActionExecutor(ABC):
    """Execute a named action with a given payload and context."""

    @abstractmethod
    async def execute(self, action: Action, ctx: OrchestrationContext) -> Result:
        raise NotImplementedError


class StateStore(ABC):
    """Persist and retrieve orchestration state."""

    @abstractmethod
    async def get(self, key: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        raise NotImplementedError


class EventBus(ABC):
    """Publish and subscribe to orchestration events."""

    @abstractmethod
    async def publish(self, event_name: str, payload: Any) -> None:
        raise NotImplementedError


class AgentInterface(ABC):
    """Abstract agent capable of handling Tasks and producing Actions or Results."""

    @abstractmethod
    async def handle_task(self, task: Task, ctx: OrchestrationContext) -> Iterable[Action]:
        raise NotImplementedError


class OrchestratorInterface(ABC):
    """Coordinate Agents, ActionExecutors, StateStore and EventBus to run tasks."""

    @abstractmethod
    async def run_task(self, task: Task, agent_config: AgentConfig) -> Result:
        raise NotImplementedError

    @abstractmethod
    def register_agent(self, agent_id: str, agent: AgentInterface) -> None:
        raise NotImplementedError
```

Documentation summary for each ABC is included in docstrings.

---

### Orchestrator agnostic base layer

File: app/agents/orchestrator/base.py

- Provide a thin coordinator that composes core components:
    - OrchestratorBase implements common wiring (register_agent, default StateStore/EventBus injection).
    - Expose lifecycle hooks: on_task_start, on_action_dispatched, on_task_complete.

Example minimal base

```
from typing import Dict
from app.agents.core.interfaces import OrchestratorInterface, AgentInterface, StateStore, EventBus, ActionExecutor
from app.agents.core.models import Task, AgentConfig, Result


class OrchestratorBase(OrchestratorInterface):
    def __init__(self, state_store: StateStore, event_bus: EventBus, action_executor: ActionExecutor):
        self._agents: Dict[str, AgentInterface] = {}
        self._state = state_store
        self._events = event_bus
        self._executor = action_executor

    def register_agent(self, agent_id: str, agent: AgentInterface) -> None:
        self._agents[agent_id] = agent

    async def run_task(self, task: Task, agent_config: AgentConfig) -> Result:
        # common orchestration lifecycle implemented here using core ABCs
        ...
```

Keep orchestration flow in base as much as possible; framework adapters implement low-level agent call semantics and any SDK-specific behavior.

---

### crewai adapter design

Files under app/agents/orchestrator/crewai/

- agent_adapter.py
    - Implements AgentInterface by wrapping crewai agent primitives.
    - Translates Task -> crewai request and crewai response -> Iterable[Action].

- orchestrator.py
    - Subclass of OrchestratorBase that includes crewai client initialization and maps base lifecycle hooks to crewai events if necessary.
    - Implements any crewai-specific concurrency, streaming, or callback behavior.

Key points:

- Keep all crewai imports inside the crewai package — core must remain import-free of crewai.
- Provide configuration via AgentConfig or explicit adapter factory.
- Provide synchronous and asynchronous execution modes depending on crewai SDK.

Example agent_adapter skeleton

```
# app/agents/orchestrator/crewai/agent_adapter.py
from app.agents.core.interfaces import AgentInterface, OrchestrationContext
from app.agents.core.models import Task, Action


# import crewai SDK inside this module
# from crewai import Client, CrewAgent

class CrewaiAgentAdapter(AgentInterface):
    def __init__(self, crew_client, crew_agent_name: str):
        self._client = crew_client
        self._agent_name = crew_agent_name

    async def handle_task(self, task: Task, ctx: OrchestrationContext):
        # call crewai SDK to run the agent
        # parse response and yield Action instances
        ...
```

---

### Interface documentation guidance

Create human-friendly docs in app/agents/core/README.md and docstrings for each ABC.

Essential doc points for core README:

- Purpose: what belongs in core vs orchestrator.
- Contract expectations: which methods must be implemented, sync vs async expectations, how errors should be modeled (raise exceptions vs return Result.error).
- Examples: minimal fake implementations for testing.
- Evolution guidance: when to add methods vs create new interfaces.

Essential doc points for orchestrator README:

- How to implement an adapter for a new framework:
    - Implement AgentInterface for the framework's agent primitive.
    - Implement ActionExecutor if framework provides tools/skills.
    - Plug into OrchestratorBase or subclass to adapt lifecycle hooks.
- Example of wiring crewai adapter with in-memory StateStore and simple EventBus.

---

### Testing strategy

- Unit tests for each core ABC using small fake implementations.
    - FakeStateStore, FakeEventBus, FakeActionExecutor to validate OrchestratorBase behaviors.
- Integration test for crewai:
    - If crewai has a test/stub client, use it; otherwise mock crewai client calls.
    - E2E test: register CrewaiAgentAdapter, run a Task, assert returned Result and state transitions.
- Add static typing checks and linters.

---

### Minimal example of a fake implementation for tests

```
# app/agents/core/tests/fakes.py
from app.agents.core.interfaces import ActionExecutor, StateStore, EventBus, AgentInterface
from app.agents.core.models import Action, Task, OrchestrationContext, Result


class InMemoryStateStore(StateStore):
    def __init__(self):
        self.store = {}

    async def get(self, key: str): return self.store.get(key)

    async def set(self, key: str, value): self.store[key] = value


class InMemoryEventBus(EventBus):
    def __init__(self):
        self.events = []

    async def publish(self, event_name: str, payload):
        self.events.append((event_name, payload))


class SimpleActionExecutor(ActionExecutor):
    async def execute(self, action: Action, ctx: OrchestrationContext) -> Result:
        return Result(success=True, output={"executed": action.name})
```

---

### Initial implementation milestones

1. Day 1–2: scaffold core package, models, and interfaces with docstrings and README.
2. Day 3–5: implement OrchestratorBase, simple in-memory StateStore/EventBus, ActionExecutor fake, and unit tests.
3. Day 6–10: implement crewai adapter (agent_adapter and orchestrator) and integration tests with mocked crewai.
4. Day 11–14: polish docs, CI, type checks, and create langchain adapter skeleton.

---

### Final notes

- Keep core stable and small; only add new methods when strictly required.
- Make adapter boundaries explicit and well-documented so new orchestrators only implement a small surface.
- Prefer async ABCs for scalability; provide sync wrapper helpers for simple scripts.
