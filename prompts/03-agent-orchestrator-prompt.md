Given the following project structure

```
agentic-knowledge-base/
├── environment.yml
├── Makefile
├── README.md
├── app/
│   ├── __init__.py
│   ├── agents/
│   │   ├── core/
│   │   ├── intelligence/
│   │   ├── knowledge/
│   │   ├── orchestrator/
│   │   ├── planner/
│   │   ├── research/
│   │   └── retrieval/
│   └── integration/
│       ├── documentation/
│       ├── llm/
│       ├── scraper/
│       ├── search/
│       └── vectordb/
```

Put the orchestrator logic in `app/agents/orchestrator/`.
Put any abstract logic (i.e. framework agnostic logic) in `app/agents/core/`.
Put any agent specific logic in `app/agents/`.
Come up with a plan to build the agent orchestrator for an autonomous RAG knowledge base system using open-source tools with the following agents:

* planners
* intelligence
* knowledge
* research
* retrieval

Do not write any code. Come up with a detailed plan only.
