Given the following project structure

```
agentic-knowledge-base/
│
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   └── __init__.py
│   │   ├── intelligence/
│   │   │   └── __init__.py
│   │   ├── knowledge/
│   │   │   └── __init__.py
│   │   ├── orchestrator/
│   │   │   ├── crewai/
│   │   │   │   └── __init__.py
│   │   │   └── langchain/
│   │   │       └── __init__.py
│   │   ├── planner/
│   │   │   └── __init__.py
│   │   ├── research/
│   │   │   └── __init__.py
│   │   └── retrieval/
│   │       └── __init__.py
```

Put the orchestrator logic in `app/agents/orchestrator/`.
Put any abstract logic (i.e. framework agnostic logic) in `app/agents/core/`.
We are not interested in agent-specific logic in this plan, so we will not put anything in `app/agents/`.
Make enough abstraction to support both `crewai` and `langchain` orchestrators.
We are going to aim for `crewai` as the initial implementation.

Come up with an implementation plan.
Do not write any code. Come up with a detailed plan only.
