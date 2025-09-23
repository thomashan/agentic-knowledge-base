# Orchestrator implementation plan & core ABCs

> Purpose: design an orchestrator layer placed in `app/agents/orchestrator/` with framework-agnostic core abstractions in `app/agents/core/` so both `crewai` (initial implementation) and `langchain` implementations are
> supported.

---

## High-level goals

1. Provide **framework-agnostic** abstractions for defining workflows, tasks, execution contexts, persistence, and eventing.
2. Implement a **crewai** orchestrator adapter as the first concrete orchestrator in `app/agents/orchestrator/crewai/`.
3. Make it straightforward to add `langchain` (or other) adapters by implementing small adapter layers and reusing core ABCs.
4. Emphasise testability, observability, and clear boundaries between core orchestration logic and adapter-specific details.

## Constraints and assumptions

* We will not implement agent-specific logic in `app/agents/` for now — orchestrator and core should be agent-agnostic.
* The orchestrator must support both synchronous and asynchronous task execution, retries, basic branching, and parallel nodes.
* Persistence (runs, tasks, logs) should be abstracted so multiple backing stores (in-memory, file, DB) are possible.
* Initial implementation target: a minimal, working `crewai` adapter that can run simple workflows (linear + parallel + simple branching).

---

## Top-level directory responsibilities

```
app/agents/
├── core/           # framework-agnostic abstractions (ABCs), small helpers
├── orchestrator/   # concrete orchestrator implementations and adapter glue
│   ├── crewai/     # crewai integration
│   └── langchain/  # langchain integration (future)
```

* `app/agents/core/` — defines the core interfaces (ABCs), small default implementations, data models, and utility types.
* `app/agents/orchestrator/crewai/` — crewai adapter implementing the orchestrator ABC using crewai's API/SDK.
* `app/agents/orchestrator/langchain/` — adapter implementing the same orchestrator ABC mapping to LangChain constructs.

---

## Phased implementation plan

### Phase 0 — Design & scaffolding (1–2 days)

* Create `app/agents/core/` and `app/agents/orchestrator/crewai/` packages.
* Write the core ABCs (see below) and small in-memory reference implementations.
* Add typing and docstrings.

### Phase 1 — Core features (3–5 days)

* Implement `WorkflowSpec`, `TaskSpec`, `ExecutionContext`, `TaskResult`, `RunStore` ABCs.
* Implement an in-memory `RunStore` and `EventBus` for local testing.
* Unit tests for core behavior (scheduling, retries, status transitions).

### Phase 2 — Crewai adapter (3–7 days)

* Implement `CrewaiOrchestrator` adapter that implements `OrchestratorABC` by translating `WorkflowSpec` and `TaskSpec` to crewai concepts.
* Implement minimal executor that can run tasks via crewai SDK (or HTTP) and collect results into `RunStore`.
* Integration tests (mocked crewai responses). Small demo workflows.

### Phase 3 — Production hardening (2–4 days)

* Add persistent `RunStore` (Postgres / SQLite) implementations.
* Add metrics hooks and structured logs.
* Add retry/backoff policies, timeouts, rate limiting, cancelation logic.

### Phase 4 — LangChain adapter & features (2–5 days)

* Implement `LangChainOrchestrator` adapter mapping core specs to LangChain run/execution model.
* Port example workflows and run integration tests.

### Phase 5 — UX & Developer ergonomics (ongoing)

* Add CLI tools for submitting workflows and checking runs.
* Add YAML/JSON workflow definitions and a small validation CLI.
* Add examples and README documentation.

> Note: time buckets are rough estimates for planning and prioritisation, not promises of delivery.

---

# Core ABCs (design + example code)

Below are the framework-agnostic abstractions to live in `app/agents/core/`.

**File:** `app/agents/core/abc.py`

```
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol
from enum import Enum
import datetime


class Status(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class TaskSpec:
    id: str
    name: str
    inputs: Dict[str, Any]
    metadata: Dict[str, Any] = None
    timeout_seconds: Optional[int] = None


@dataclass
class TaskResult:
    task_id: str
    status: Status
    output: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None


@dataclass
class TaskNode:
    id: str
    spec: TaskSpec
    depends_on: List[str]
    retry_policy: Optional[Dict[str, Any]] = None
    parallelism: int = 1
    hints: Dict[str, Any] = None  # orchestrator-specific hints


@dataclass
class WorkflowSpec:
    id: str
    name: str
    nodes: List[TaskNode]
    edges: List[tuple[str, str]]  # list of (from_node_id, to_node_id)
    metadata: Dict[str, Any] = None


class ExecutionContext(ABC):
    """Read-only execution context provided to tasks and orchestrators."""

    @property
    @abstractmethod
    def workflow_id(self) -> str:
        ...

    @property
    @abstractmethod
    def run_id(self) -> str:
        ...

    @property
    @abstractmethod
    def now(self) -> datetime.datetime:
        ...

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        ...


class RunStoreABC(ABC):
    """Persistence layer for runs and tasks. Keep it small and testable."""

    @abstractmethod
    def create_run(self, workflow: WorkflowSpec, inputs: Dict[str, Any]) -> str:
        """Create a run for a workflow and return run_id."""

    @abstractmethod
    def update_task_result(self, run_id: str, task_result: TaskResult) -> None:
        ...

    @abstractmethod
    def get_task_result(self, run_id: str, task_id: str) -> Optional[TaskResult]:
        ...

    @abstractmethod
    def set_run_status(self, run_id: str, status: Status) -> None:
        ...

    @abstractmethod
    def get_run_status(self, run_id: str) -> Status:
        ...


class EventBusABC(ABC):
    """Simple pub/sub for orchestration events.

    Implementations can be in-memory for tests or backed by redis/pubsub in prod.
    """

    @abstractmethod
    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def subscribe(self, topic: str, handler) -> None:
        ...


class SchedulerABC(ABC):
    """Component responsible for scheduling and executing tasks.

    The scheduler is deliberately small: it translates TaskSpec -> execution and
    reports TaskResult back to RunStore.
    """

    @abstractmethod
    def schedule_task(self, run_id: str, node: TaskNode, ctx: ExecutionContext) -> str:
        """Schedule a task and return a task_run_id (opaque)."""

    @abstractmethod
    def cancel_task(self, task_run_id: str) -> None:
        ...

    @abstractmethod
    def get_task_status(self, task_run_id: str) -> Status:
        ...


class OrchestratorABC(ABC):
    """Top-level orchestrator interface. Concrete adapters (crewai, langchain)
    must implement this and map core Workflow/Task concepts to framework specifics.
    """

    @abstractmethod
    def deploy_workflow(self, workflow: WorkflowSpec) -> str:
        """Make a workflow known to the orchestrator (returns an id).

        For simple adapters this could be a no-op that returns workflow.id.
        """

    @abstractmethod
    def start_run(self, workflow_or_id: WorkflowSpec | str, inputs: Dict[str, Any]) -> str:
        """Start a run and return run_id."""

    @abstractmethod
    def get_run_status(self, run_id: str) -> Status:
        ...

    @abstractmethod
    def cancel_run(self, run_id: str) -> None:
        ...

    @abstractmethod
    def get_task_result(self, run_id: str, task_id: str) -> Optional[TaskResult]:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Graceful shutdown for resources (connections, threads)."""
```

---

## Small helper types & default implementations

Add a `app/agents/core/in_memory_store.py` providing a `RunStoreInMemory` that implements `RunStoreABC` used for unit tests and local dev. Similarly provide `SimpleEventBus` in `app/agents/core/event_bus.py`.

---

## Adapter contract (orchestrator → crewai/langchain)

Adapters implement `OrchestratorABC` by doing the following responsibilities:

1. **Translating** `WorkflowSpec` and `TaskSpec` into the adapter's runtime concepts.
2. **Scheduling** tasks (use `SchedulerABC` where appropriate).
3. **Translating results** from the adapter back into `TaskResult` and storing them in `RunStore`.
4. **Emitting events** on `EventBus` for lifecycle events (task-started, task-finished, run-completed).
5. **Implementing hints**: `TaskNode.hints` allows adapter-specific tuning — e.g., `crewai: { model: 'gpt-4o', concurrency: 2 }`.

### Minimal adapter glue responsibilities

* `translate_workflow(workflow_spec) -> adapter_workflow`
* `translate_task(task_spec) -> adapter_task`
* `monitor_and_forward(adapter_task_run) -> TaskResult`

---

## Example: Task lifecycle (high-level)

1. `Orchestrator.start_run()` creates a `run_id` via `RunStore.create_run(...)`.
2. The orchestrator scheduler selects ready `TaskNode`s and calls `Scheduler.schedule_task()`.
3. `Scheduler` forwards tasks to adapter runtime (crewai) and returns `task_run_id`.
4. Adapter runtime executes; the adapter monitors progress and converts lifecycle into `TaskResult`.
5. `RunStore.update_task_result()` records the outcome and orchestrator decides next nodes to schedule.
6. When no ready nodes remain, orchestrator sets run status to SUCCEEDED/FAILED.

---

## Example usage snippet (pseudo)

```
# create components
store = RunStoreInMemory()
event_bus = SimpleEventBus()
crewai = CrewaiOrchestrator(store=store, event_bus=event_bus, config=...)

# deploy workflow (optional)
workflow_id = crewai.deploy_workflow(workflow_spec)
run_id = crewai.start_run(workflow_id, inputs={})

# poll
status = crewai.get_run_status(run_id)
```

---

## Example YAML workflow format (developer ergonomics)

```yaml
id: example_linear
name: example linear workflow
nodes:
  - id: n1
    name: generate
    inputs:
      prompt: "Write hello world"
  - id: n2
    name: summarize
    depends_on: [ n1 ]
edges: [ ]
```

Add small validation: ensure node ids unique, `depends_on` valid, no cycles (or explicit cycles allowed with special semantics).

---

## Observability & operational concerns

* Emit structured events for: `task.started`, `task.succeeded`, `task.failed`, `run.started`, `run.succeeded`, `run.failed`.
* Integrate metrics hooks (counts + latency) into core interfaces — provide `MetricsCollectorABC` to plug in Prometheus or in-memory.
* Make logs structured and attach `run_id`/`task_id` to each log line.

---

## Failure modes & design decisions

* **Idempotency:** tasks should be idempotent; orchestrator must support retries and deduplication where possible.
* **Exactly-once vs at-least-once:** start with *at-least-once* delivery model and document caveats; add deduplication later.
* **State persistence:** store minimal task outputs required to resume runs.
* **Backpressure:** adapter should expose concurrency limits via `TaskNode.hints` and scheduler should respect them.

---

## Tests to write

1. Unit tests for core ABC implementations (in-memory run store, event bus).
2. Scheduler unit tests: scheduling readiness evaluation, retry handling.
3. Crewai adapter integration tests (mock crewai SDK) covering happy path and error paths.
4. End-to-end test running a small workflow with the in-memory store.

---

## Documentation to ship

* `README.md` in `app/agents/orchestrator/` explaining the design, how to implement a new adapter, and example workflows.
* `doc/` with sequence diagrams for task lifecycle and adapter flows.
* API docstrings on each ABC method (see code above).

---

## Next steps / recommended first PR content

1. Add `app/agents/core/abc.py` with the code above and basic type imports.
2. Add `app/agents/core/in_memory_store.py` and `event_bus.py` with simple implementations.
3. Add small test suite verifying the run-store and event bus.
4. Create `app/agents/orchestrator/crewai/` skeleton implementing `OrchestratorABC` but using the in-memory store to run a trivial pass-through.

---

If you'd like, I can also:

* Produce ready-to-drop Python files for `abc.py`, `in_memory_store.py` and `event_bus.py`.
* Provide a starter `crewai` adapter skeleton implementing the minimal methods above.

Tell me which file you'd like first and I'll add the implementation.
