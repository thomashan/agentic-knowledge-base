Feed in responses from

* `propmts/chatgpt/idea-deep-research.md`
* `propmts/claude/idea-opus-4.1-extended-thinking.md`
* `propmts/copilot/idea-deep-research.md`
* `propmts/deepseek/idea-deepthink-search.md`
* `propmts/gemini/idea-ai-studio.md`
* `propmts/gemini/idea-gemini-pro-deep-research.md`
* `propmts/grok/grok-expert.md`
* `propmts/qwen/idea-qwen3-235b-a22b-2507.md`

These are some initial architectural recommendations from various AI models.

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

Include the directory structure.
Write a detailed plan for each component (i.e. agent orchestration, research agent, etc.) and recommended sequence of steps for implementation.
Focus on the core components to make it run end-to-end locally.
The first step is to get the AI orchestrator running.
Leave out the foundational components (i.e. kubernetes, monitoring, etc.) as the last step.
Do not write any code.
