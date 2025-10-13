# Decisions

Based on the LLM recommendation in `prompts/**/idea-*.md` the following decisions were made.

| platform/tool                      | decision                 |  
|------------------------------------|--------------------------|
| agent orchestration                | CrewAI                   |
| research agent web search API      | API agnostic             |
| research agent web crawler/scraper | Crawler/Scraper agnostic |
| documentation platform             | tool agnostic            |
| vectorDB                           | Qdrant                   |
| infra                              | Docker, Kubernetes       |
| monitoring                         | Grafana, Prometheus      |
| planner agent LLM                  | LLM agnostic             |
| research agent LLM                 | LLM agnostic             |
| intelligence agent LLM             | LLM agnostic             |
| knowledge agent LLM                | LLM agnostic             |
| retrieval agent LLM                | LLM agnostic             |

Although many of the choices are agnostic, there are upfront decisions that need to be made.
Namely, CrewAI for agent orchestration, Qdrant for vectorDB, Docker/Kubernetes for infra, and Grafana/Prometheus for monitoring.

## Platform/Tool Agnostic Decisions

Whilst some platform/tool are agnostic, initial implementation decisions have to be made.

| platform/tool                      | initial implementation   |  
|------------------------------------|--------------------------|
| agent orchestration                | CrewAI                   |
| research agent web search API      | SearXNG                  |
| research agent web crawler/scraper | AgenticSeek              |
| documentation platform             | Outline                  |
| all LLMs                           | start with Llama 3.2 11B |

## Project structure

None of the LLM responses really fit into the structure I was thinking.
I came up with the following structure.

```
agentic-knowledge-base/
├── app/
│   ├── agents-core/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── agents_core/
│   │           ├── __init__.py
│   │           └── core.py
│   │   └── tests/
│   │       └── test_core.py
│   │
│   ├── agents-orchestrator/
│   │   ├── crewai/
│   │   │   ├── pyproject.toml
│   │   │   └── src/
│   │   │       └── crewai_adapter/
│   │   │           └── adapter.py
│   │   │   └── tests/
│   │   │       └── ...
│   │   └── factory/
│   │       ├── pyproject.toml
│   │       └── src/
│   │           └── factory/
│   │               └── factory.py
│   │
│   └── (agents-intelligence, etc.)
│
├── pyproject.toml
├── README.md
└── uv.lock
```
