# Implementation Plan

---

## Overview

We’ll define a clear abstraction layer in `app/agents/core` to represent orchestrator behaviors, then build a CrewAI-based orchestrator under `app/agents/orchestrator/crewai`. We’ll also scaffold a LangChain adapter in
`app/agents/orchestrator/langchain` without implementation. This modular design guarantees both present support and future swappability.

---

## Goals and Constraints

- Encapsulate all framework-agnostic logic in `app/agents/core`.
- Place only framework-specific code under each orchestrator subfolder.
- Ensure both CrewAI and LangChain orchestrators conform to the same interface.
- CrewAI will be the first concrete implementation; LangChain remains a stub.

---

## Directory Responsibilities

| Directory                         | Purpose                                                             |
|-----------------------------------|---------------------------------------------------------------------|
| app/agents/core                   | Define abstract orchestrator interfaces; common types; error models |
| app/agents/orchestrator/crewai    | Implement CrewAI orchestrator adapter                               |
| app/agents/orchestrator/langchain | Scaffold LangChain adapter; mirror interface                        |

---

## 1. Define Core Abstractions (`app/agents/core`)

1. Identify core concepts
    - Orchestrator interface: methods like `initialize()`, `dispatch_tasks()`, `handle_results()`.
    - Data contracts: `Task`, `Result`, `OrchestrationContext`.
    - Error hierarchy and retry strategies.

2. Draft interfaces and types
    - Use Python `Protocol` or abstract base classes to define method signatures.
    - Define plain-data classes for tasks and contexts.

3. Create utility modules
    - Logging helper with structured logs.
    - Event dispatcher or callback registry.

---

## 2. Design Orchestrator Interface

1. Define minimal public API
    - `Orchestrator.start(context: OrchestrationContext) -> None`
    - `Orchestrator.step() -> List[Task]`
    - `Orchestrator.complete(task_results: List[Result]) -> None`

2. Specify lifecycle hooks
    - Setup and teardown
    - Pre- and post-dispatch event hooks

3. Document interface contracts
    - Parameter invariants
    - Expected exceptions and recovery paths

---

## 3. Implement CrewAI Adapter (`app/agents/orchestrator/crewai`)

1. Configuration
    - Parse CrewAI credentials and endpoint from environment or config file.

2. Adapter class
    - Subclass core `Orchestrator` interface.
    - Map core `Task` to CrewAI payload schema.
    - Invoke CrewAI SDK or HTTP client.
    - Translate CrewAI responses into core `Result` objects.

3. Error handling
    - Wrap CrewAI errors in core exception types.
    - Implement retry according to core retry policy.

4. Integration points
    - Hook into core logging and event system.

---

## 4. Scaffold LangChain Adapter (`app/agents/orchestrator/langchain`)

1. Create adapter stub with identical class signature
2. Raise `NotImplementedError` in each method
3. Add TODO markers pointing to core API
4. Ensure unit tests can import without errors

---

## 5. Testing Strategy

1. Unit tests for core abstractions
    - Validate interface compliance
    - Test data contracts and error models

2. Mocked integration tests for CrewAI
    - Simulate successful task dispatch and result translation
    - Simulate CrewAI failures and retries

3. Interface consistency tests
    - Verify both adapters satisfy the `Orchestrator` protocol

---

## 6. Documentation and Onboarding

- Update README with orchestrator architecture overview
- Write doc-strings on interfaces and adapters
- Create a “How to add a new orchestrator” guide
- Diagram call flow: core → adapter → external service → core

---

## 7. CI/CD and Deployment

- Add linting and type-checking for core and adapter modules
- Integrate tests into CI pipeline
- Configure environment variables for CrewAI secrets in staging and prod
- Automate deployments with versioned releases of orchestrator package

---

This plan establishes a robust abstraction in `core`, a concrete CrewAI implementation, and a future-ready LangChain scaffold. From here, focus on interface design and iterative adapter development to keep the entire
orchestrator layer modular and swappable.
