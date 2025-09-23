Given the following project structure

```
agentic-knowledge-base/
│
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   └── __init__.py
│   │   ...
│   │   ├── orchestrator/
│   │   │   ├── crewai/
│   │   │   │   └── __init__.py
│   │   │   └── langchain/
│   │   │       └── __init__.py
```

Put the orchestrator logic in `app/agents/orchestrator/`.
Put any abstract logic (i.e. framework agnostic logic) in `app/agents/core/`.
We are not interested in agent-specific logic in this plan, so we will not put anything in `app/agents/`.
Make enough abstraction to support both `crewai` and `langchain` orchestrators.
We are going to aim for `crewai` as the initial implementation.

Come up with an implementation plan.
Come up with ABC definitions and documentation for core and orchestrator agnostic interfaces.
