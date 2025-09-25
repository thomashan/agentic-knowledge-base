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
├── .gitignore
├── .python-version
├── environment.yml
├── Makefile
├── pyproject.toml
├── README.md
├── uv.lock
├── .gemini/...
├── .git/...
├── .github/
│   └── workflows/
│       ├── make.yml
│       └── test-build.yml
├── .idea/...
├── app/
│   ├── agents-core/
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   └── agents_core/
│   │   │       └── core.py
│   │   └── tests/
│   │       └── test_core.py
│   ├── agents-intelligence/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agents_intelligence/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── agents-knowledge/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agents_knowledge/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── agents-orchestrator-crewai/
│   │   ├── .DS_Store
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   └── crewai_adapter/
│   │   │       ├── __init__.py
│   │   │       └── adapter.py
│   │   └── tests/
│   │       ├── test_adapter.py
│   │       └── test_integration_adapter.py
│   ├── agents-orchestrator-factory/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   └── factory/
│   │   │       ├── __init__.py
│   │   │       └── factory.py
│   │   └── tests/
│   │       └── test_factory.py
│   ├── agents-orchestrator-langchain/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── langchain_adapter/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── agents-planner/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agents_planner/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── agents-research/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agents_research/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── agents-retrieval/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agents_retrieval/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── integration-documentation/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── integration_documentation/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── integration-llm/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── integration_llm/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── integration-scraper/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── integration_scraper/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── integration-search/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── integration_search/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   ├── integration-vectordb/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── integration_vectordb/
│   │   │       └── __init__.py
│   │   └── tests/
│   │       └── __init__.py
│   └── runner/
│       ├── pyproject.toml
│       ├── src/
│       │   └── agentic_knowledge_base_runner/
│       │       └── main.py
│       └── tests/
│           └── __init__.py
├── config/
│   └── config.mk
├── docs/
│   ├── crewai_orchestrator.md
│   └── decisions.md
└── prompts/
    ├── 01-idea-prompt.md
    ├── 02-initial-implementation-prompt.md
    ├── 03-agent-orchestrator-prompt.md
    ├── 04-agent-orchestrator-refined-prompt.md
    ├── 05-agent-orchestrator-interface-prompt.md
    ├── 06-agent-orchestrator-interface-implementation-plan-prompt.md
    ├── 07-agent-orchestrator-implementation-prompt.md
    ├── chatgpt/
    │   ├── 01-idea-deep-research.md
    │   ├── 02-initial-implementation-deep-research.md
    │   ├── 03-agent-orchestrator-think.md
    │   ├── 04-agent-orchestrator-refined-think.md
    │   └── 05-agent-orchestrator-interfaces-think.md
    ├── claude/
    │   ├── 01-idea-opus-4.1-extended-thinking.md
    │   ├── 02-initial-implementation-opus-4.1.md
    │   ├── 03-agent-orchestrator-sonnet-4.md
    │   ├── 04-agent-orchestrator-refined-sonnet-4.md
    │   └── 05-agent-orchestrator-interfaces-sonnet-4.md
    ├── copilot/
    │   ├── 01-idea-deep-research.md
    │   ├── 02-initial-implementation-smart.md
    │   ├── 03-agent-orchestrator-think-deeper.md
    │   ├── 04-agent-orchestrator-refined-think-deeper.md
    │   └── 05-agent-orchestrator-interface-think-deeper.md
    ├── deepseek/
    │   ├── 01-idea-deepthink-search.md
    │   ├── 02-initial-implementation-deepthink.md
    │   ├── 03-agent-orchestrator-deepthink.md
    │   ├── 04-agent-orchestrator-refined-deepthink.md
    │   └── 05-agent-orchestrator-interface-deepthink.md
    ├── gemini/
    │   ├── 01-idea-ai-studio.md
    │   ├── 01-idea-gemini-2.5-pro-deep-research.md
    │   ├── 02-initial-implementation-gemini-2.5-pro-deep-research.md
    │   ├── 03-agent-orchestrator-gemini-2.5-pro.md
    │   ├── 04-agent-orchestrator-refined-gemini-2.5-pro.md
    │   └── 05-agent-orchestrator-interface-gemini-2.5-pro-deep-research.md
    ├── gemini-cli/
    │   ├── 06-agent-orchestrator-interface-implementation-plan-gemini-2.5-pro.md
    │   └── 07-agent-orchestrator-implementation-gemini-cli.md
    ├── grok/
    │   ├── 01-idea-grok-expert.md
    │   ├── 02-initial-implementation-expert.md
    │   ├── 03-agent-orchestrator-expert.md
    │   ├── 04-agent-orchestrator-refined-expert.md
    │   └── 05-agent-orchestrator-interface-expert.md
    ├── qwen/
    │   ├── 01-idea-qwen3-235b-a22b-2507.md
    │   ├── 02-initial-implementation-qwen3-235b-a22b-2507.md
    │   ├── 03-agent-orchestrator-qwen3-235b-a22b-2507-thinking.md
    │   ├── 04-agent-orchestrator-refined-qwen3-235b-a22b-2507-thinking.md
    │   └── 05-agent-orchestrator-interface-qwen3-235b-a22b-2507-thinking.md
    └── template/
        ├── gemini-plan-example.md
        ├── README.md
        └── vibe-coding-template-example.md
```
