# Implementation plan — Orchestrator + Core (no code)

Nice — here’s a focused, practical plan for implementing the orchestrator layer inside `app/agents/orchestrator/` while keeping framework-agnostic logic in `app/agents/core/`. I’ll describe architecture, abstractions,
interfaces/contracts, module responsibilities, testing, deployment/operational concerns, and a clear step-by-step execution checklist you can follow. I deliberately keep everything design/plan-only (no code) as you
requested.

---

## Goals & constraints

* Keep **all orchestrator-specific code** under `app/agents/orchestrator/` (initial: `crewai`, future: `langchain`).
* Put **framework-agnostic orchestration logic** (scheduling, state machine, retries, serialization, message schemas, validation, tracing) in `app/agents/core/`.
* Provide a clear adapter contract so `crewai` and `langchain` implementations can be swapped.
* Implement `crewai` adapter first; plan must make month-2+ `langchain` adapter straightforward.
* Provide strong testing and contract tests so both adapters behave the same from the rest of the app’s perspective.
* No agent-specific logic in top-level `app/agents/` (it will remain empty aside from packages).

---

## High-level architecture

1. **Core layer (`app/agents/core/`) — framework-agnostic**

    * Domain models & schemas (Plan, Task, TaskResult, AgentMessage, ExecutionTrace, PlanState).
    * Orchestration engine: state machine for plan lifecycle (created → running → paused → completed → failed → cancelled).
    * Scheduler/executor abstraction (interface) that can call a concrete adapter.
    * Utilities: serialization, idempotency helpers, retry policy, backoff, validation.
    * Contract tests / mock harness for adapters.

2. **Orchestrator adapters (`app/agents/orchestrator/`)**

    * `crewai` adapter: concrete implementation of the adapter contract; integrates with CrewAI client APIs, maps domain models -> CrewAI calls and back.
    * `langchain` adapter: secondary implementation, same contract, to be added later.

3. **Integration points**

    * Upstream: `planner`, `intelligence`, `knowledge`, `retrieval`, `research` modules call orchestrator via the core public interface (e.g., `orchestrate(plan)`).
    * Downstream/agents: concrete orchestrator adapters send messages/requests to actual agent runtimes (CrewAI or LangChain).

4. **Persistence / state**

    * Abstract persistence interface in core (so you can plug DB, file, or in-memory store).
    * Orchestrator persists Plan states, checkpoints, traces, task history.

5. **Observability**

    * Structured logging and traces emitted from core; adapters add implementation-specific logs.
    * Metrics interface (events: plan\_started, task\_failed, retry, plan\_completed).

---

## Core abstractions & public contract (conceptual)

> These are design contracts — define them precisely in code later (types, docstrings).

### Domain models

* `Plan` — top-level unit of orchestration (id, metadata, root tasks, inputs, owner, created\_at).
* `Task` — atomic unit (id, type, payload, dependencies, retry\_policy, attempt\_count, status).
* `TaskResult` — result container (task\_id, success boolean, output, diagnostics).
* `ExecutionTrace` — chronological logs/events for a plan (task dispatched, response received, errors).
* `PlanState` — persisted snapshot of `Plan` and all `Task` states.

### Core interfaces (abstract)

* `Orchestrator` (core-facing): main programmatic interface used by other modules.

    * `submit_plan(plan_descriptor) -> plan_id`
    * `get_plan(plan_id) -> PlanState`
    * `cancel_plan(plan_id) -> bool`
    * `resume_plan(plan_id) -> bool`
    * `list_plans(filter) -> [PlanState]`
    * `stream_plan_events(plan_id)` (optional, for live UI)
* `ExecutionAdapter` (adapter-facing, implemented by crewai/langchain)

    * `dispatch_task(task: Task) -> TaskHandle` — send task to an agent runtime; returns handle to track
    * `get_task_result(handle: TaskHandle) -> TaskResult` — poll / fetch result
    * `cancel_task(handle: TaskHandle) -> bool`
    * `adapter_health_check() -> HealthStatus`
* `Persistence` (pluggable store)

    * `save_plan_state(plan_state)`
    * `load_plan_state(plan_id)`
    * `append_execution_trace(plan_id, trace_event)`
* `Scheduler` (internal: can be synchronous, threaded, or async)

    * Responsible for selecting ready tasks, enforcing concurrency limits, applying backoff.

### Failure and semantics

* Core enforces idempotency: if a task is retried, the adapter must be able to deduplicate or core must detect duplicates via task idempotency keys.
* Clear retry semantics configured per-task (max\_retries, backoff, jitter).
* Tasks must be serializable so plan checkpoints can be restored.

---

## Module layout (file-level plan)

(keep only code for orchestration in these paths)

```
app/agents/core/
├── models/                # domain models (Plan, Task, TaskResult, Trace) — framework-agnostic
├── orchestrator/          # pure orchestration engine (state machine, scheduler)
├── persistence/           # persistence interface + in-memory/mock impl for tests
├── adapter/               # adapter interface definitions (ExecutionAdapter)
├── policies/              # retry/backoff/idempotency policies
├── utils/                 # validation, serialization, logging helpers
└── tests/                 # unit and contract tests for the core

app/agents/orchestrator/
├── crewa i/               # adapter implementing ExecutionAdapter for CrewAI (initial)
│   ├── client_wrapper/    # CrewAI client glue code & transform utilities
│   ├── adapter_impl.py    # maps Task <-> CrewAI calls
│   └── tests/             # integration/adapter tests (use a mock CrewAI server)
└── langchain/             # future adapter (same structure)
```

---

## Execution flow (detailed step-by-step)

1. **Plan submission**

    * Caller constructs a `Plan` descriptor (tasks, dependencies, metadata) and calls `Orchestrator.submit_plan()`.
    * Core validates plan schema and persists an initial `PlanState` (status `created`).

2. **Scheduling**

    * Scheduler inspects persisted plan and finds tasks with dependencies satisfied (ready tasks).
    * Scheduler enqueues ready tasks for dispatch respecting concurrency limits.

3. **Dispatch**

    * For each ready task, core constructs adapter-friendly payload and calls `ExecutionAdapter.dispatch_task(task)`.
    * Adapter returns a `TaskHandle` (opaque token) which core records in Task metadata.

4. **Monitoring / Polling / Callback**

    * Two possible models (both supported via adapter):

        * **Polling**: core periodically calls `get_task_result(handle)`.
        * **Callback/Webhook**: adapter calls core’s endpoint/event handler when a result arrives. (Core exposes event endpoint or message queue consumer.)
    * When result arrives, core stores `TaskResult`, appends trace, updates Task status.

5. **Task completion / failure**

    * On success: core marks task completed, triggers dependent tasks to become ready.
    * On failure: core consults task retry policy; if allowed, schedules retry; else marks task failed and transitions plan to failed if unrecoverable.

6. **Plan checkpointing**

    * Core persists state at important boundaries (after each task completion/failure) so plans can be resumed if restarted.

7. **Completion**

    * When all tasks completed successfully, plan status becomes `completed`. Core emits `plan_completed` metric and archive snapshot.

---

## Adapter design details (CrewAI initial)

* **Responsibility**: translate Task -> CrewAI request, map CrewAI response -> TaskResult, handle authentication and rate limits, support both polling and webhook callback modes offered by CrewAI.
* **Implementation notes**:

    * Adapter implements `ExecutionAdapter` interface.
    * Provide an adapter config object (endpoint, API key, concurrency limits, webhook secret).
    * Provide adapter-specific health check and metrics.
    * Provide an integration-test harness: a lightweight mock CrewAI service (or recorded HTTP fixtures) for CI tests.

---

## Data persistence & state management

* **Persistence interface** in core must be minimal and pluggable:

    * implementations: in-memory (for unit tests), file-based JSON/SQLite (dev), PostgreSQL (prod).
* Persist:

    * plan descriptor and task states
    * task handles returned by adapters
    * execution traces (append-only)
    * metadata for idempotency (task id -> last processed result signature)
* Plan restore:

    * load PlanState and rehydrate scheduler; re-dispatch tasks that were in-flight if adapter cannot resume them.

---

## Concurrency, scaling & orchestration semantics

* Scheduler should support configurable concurrency (global and per-plan).
* Task queue should be pluggable: in-memory queue for single-process, or a message broker (Redis/RabbitMQ/SQS) for multi-worker setups.
* Ensure task dispatch is idempotent: use unique `task_id` and `idempotency_key`.
* Provide graceful shutdown: persist in-flight tasks before exit; either cancel or let adapter continue async with callback.

---

## Error handling & retry policy

* Default retry policy (configurable per task): attempts, backoff (exponential), jitter, transient-vs-permanent error classification.
* Error types:

    * Transient adapter/network errors -> eligible for retry.
    * Permanent task errors (validation, unsupported operation) -> fail immediately.
* Error reporting:

    * Append detailed diagnostics to trace events (adapter error codes, stack traces, timestamps).
    * Surface human-friendly error messages in `PlanState`.

---

## Observability

* Structured logs (plan\_id, task\_id, event, severity, adapter, error\_code).
* Metrics to emit:

    * `plans_submitted`, `plans_completed`, `task_dispatched`, `task_completed`, `task_failed`, `retries_attempted`.
* Tracing:

    * Provide correlation IDs (plan\_id/task\_id/trace\_id) for distributed traces.
* Optionally: export traces to OpenTelemetry-compatible collector.

---

## Security & secrets

* Adapter config should read secrets from environment or a configured secret manager; never commit API keys.
* If using webhooks, verify webhook signature (adapter should provide verification utilities).
* Sanitize logs to avoid leaking secrets or user PII.

---

## Testing strategy

1. **Unit tests (core)**

    * Validate state machine transitions for plan lifecycle.
    * Validate scheduler logic for dependency resolution and concurrency limits.
    * Validate retry/backoff policies.
    * Validate persistence interface using in-memory impl.

2. **Adapter contract tests (integration-level)**

    * Implement a test harness that runs core against a mock adapter implementing the `ExecutionAdapter` (mock CrewAI).
    * These contract tests must be executed for every adapter (crewai + langchain) to prove interchangeability.

3. **Adapter integration tests (crewai)**

    * Use mocked CrewAI responses (fixtures) and, if available, a test CrewAI sandbox. Cover:

        * successful responses
        * transient errors (timeouts, 5xx)
        * permanent errors (validation)
        * webhook-based callback flows

4. **End-to-end tests**

    * Small plans that cover dependency chains, parallel tasks, retries.
    * Exercise plan restore after simulated process crash.

5. **Load & chaos tests**

    * Simulate throttling, networking flakiness, and high concurrency to validate resiliency.

6. **Contract test automation**

    * Add CI job to run core tests + adapter contract tests for any PR touching orchestrator/core or adapters.

---

## Developer experience (DX)

* Provide a simple CLI for dev testing:

    * submit plan from a JSON/YAML file
    * show plan status / tail trace
    * cancel plan
* Provide starter plan templates for common orchestration patterns.
* Provide a debug mode to run with in-memory persistence and verbose logging.

---

## CI / Release considerations (what to include in pipeline)

* Lint and static typing checks for core and adapters.
* Run core unit tests.
* Run adapter contract tests (with mock adapter).
* Run crewai adapter integration tests using HTTP fixtures / mock service.
* Package build artifacts (wheels) and publish to private index if needed.

---

## Documentation & onboarding

* Top-level `README` for `app/agents/orchestrator/` covering:

    * high-level design diagram
    * public API (Orchestrator interface)
    * How to implement a new `ExecutionAdapter`
    * How to run local dev (CLI + in-memory store)
    * Example plan descriptors
* Design doc: sequence diagrams for dispatching and callback modes, failure modes, and plan restore flow.
* Adapter README: authentication, configuration parameters, known CrewAI pitfalls and recommended limits.

---

## Acceptance criteria (concrete)

* Core exposes the `Orchestrator` interface and persists plan states.
* A `crewai` adapter exists that implements `ExecutionAdapter` and can:

    * dispatch tasks
    * receive results (polling and webhook)
    * return TaskResult objects compatible with core models
* Contract tests which prove that swapping adapters does not change the external behavior expected by callers.
* Unit and integration tests pass in CI.
* Developer docs + CLI to submit and inspect plans locally.

---

## Risks & mitigations

* **Adapter breaking changes / upgrade risk**: create thin adapter layer and pin client API versions; use adapter integration tests and fixtures.
* **In-flight task duplication on restart**: enforce idempotency keys and persist adapter task handles so we can query/lookup instead of re-dispatching.
* **State corruption**: strict schema validation and atomic persistence (DB transactions) where possible.
* **Large traces/storage growth**: rotate/paginate traces; archive completed plan snapshots to cold storage.

---

## Step-by-step implementation checklist (engineering tasks, no durations)

1. Create core skeleton in `app/agents/core/`:

    * define domain models (Plan, Task, TaskResult, Trace).
    * design and document the `Orchestrator` and `ExecutionAdapter` interface (API/contract).
2. Implement core orchestrator engine:

    * basic state machine (create, run, pause, resume, cancel, complete).
    * simple scheduler (dependency resolution) and in-memory persistence.
3. Add persistence abstraction with in-memory impl + JSON file impl.
4. Build adapter interface + a small mock adapter (for contract tests).
5. Write unit tests for core components (state transitions, scheduler, retry).
6. Implement `crewai` adapter:

    * client wrapper & request/response mapping
    * support both polling and webhook modes (adapter config)
    * adapter-specific error handling & health checks
7. Implement adapter contract tests and run with mock adapter + crewai adapter.
8. Implement CLI utilities (submit, status, tail logs).
9. Add observability hooks (structured logging, metrics interface).
10. Add integration tests that use fixtures or mocked CrewAI.
11. Add CI pipeline that runs core tests + adapter tests + linters.
12. Write docs, examples, and a design diagram.
13. Add a `langchain` adapter scaffold that implements the same interface (later fill in).

---

## What to deliver at the end of the first implementation

* `app/agents/core/` complete with models, orchestrator engine, persistence interfaces, and unit tests.
* `app/agents/orchestrator/crewai/` adapter that can dispatch tasks and return TaskResult in at least polling mode (webhook optional but recommended).
* Contract tests proving behavior parity with a mock adapter.
* Dev CLI and README explaining how to run a plan locally with the crewai adapter (using mocks/fixtures).
* CI pipeline that runs tests and lints.

---

If you want, I can now:

* convert this plan into a prioritized issue list (e.g., Jira/GitHub Issues) with atomic tasks and acceptance criteria; or
* write the adapter contract (precise method signatures & field names) so you can start implementing quickly.

Which of those would you like me to do next?
