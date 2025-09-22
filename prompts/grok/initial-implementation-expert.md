# Self-Updating Open-Source RAG Knowledge Base: Implementation Plan

This plan synthesizes the architectural recommendations from the provided AI model responses (ChatGPT, Claude Opus, Copilot, DeepSeek, Gemini AI Studio, Gemini Pro, Grok Expert, and Qwen 3.2 35B). It incorporates the
specified decisions for initial implementations while maintaining agnosticism where possible through abstraction layers. The goal is a modular, fully open-source system that runs locally, with agents operating
autonomously. All components are LLM-agnostic (starting with Llama 3.2 11B via Ollama for local inference), and the system emphasizes framework-agnostic design via adapters for easy swapping.

The plan focuses on core components to achieve an end-to-end local prototype: agent orchestration, planner agent, research agent, intelligence agent, knowledge agent, documentation platform, and retrieval agent.
Infrastructure (Docker/Kubernetes) and monitoring (Grafana/Prometheus) are deferred to the final phase. No code is provided; this is a high-level blueprint for engineers to follow.

## Key Decisions and Rationale

- **Agent Orchestration**: CrewAI (initial) for its role-based multi-agent communication and simplicity in small teams. Abstraction layer ensures swap to alternatives like LangGraph or AutoGen.
- **Research Agent Web Search API**: Agnostic (initial: SearXNG) for privacy-focused, self-hosted metasearch aggregation.
- **Research Agent Web Crawler/Scraper**: Agnostic (initial: AgenticSeek) for lightweight, LLM-driven web interaction; complements browser automation needs.
- **Documentation Platform**: Agnostic (initial: Outline) for its collaborative GUI, document-level versioning (database-backed, not Git), Markdown support, structured linking (via slugs and references), and REST API for
  machine updates. Supports text, diagrams (Mermaid/Draw.io embeds), and images.
- **Vector DB**: Qdrant for its performance in hybrid search (semantic + keyword), filtering, and scalability on small setups.
- **LLMs**: Agnostic across all agents (initial: Llama 3.2 11B) for balanced performance/privacy on local hardware. Use Ollama as the inference server with an adapter for swapping (e.g., to Mistral or Mixtral).
- **Infra/Monitoring**: Docker Compose for local runs; Kubernetes for scaling. Grafana/Prometheus for metrics/logging, added last.
- **Overall Focus**: Small-team scalability via modularity. Agents are autonomous (no handholding), with niche research spawning sub-agents dynamically. Hybrid search in retrieval. Formats: Markdown for docs, JSON for
  agent messages/artifacts.

## Directory Structure

Organize the project for modularity, with core logic in Python (no language preference, but aligns with CrewAI). Separate concerns for easy swapping.

```
self-updating-rag-kb/
├── README.md                  # Project overview, setup instructions
├── requirements.txt           # Python dependencies (e.g., crewai, ollama, qdrant-client)
├── config/                    # Configurations
│   ├── agents.yaml            # Agent roles, tools, LLM configs (YAML for CrewAI)
│   ├── llm_adapter.py         # LLM abstraction (e.g., route to Ollama/Mistral)
│   ├── db_adapter.py          # Vector DB abstraction (initial: Qdrant)
│   ├── doc_platform_adapter.py# Documentation platform abstraction (initial: Outline API)
│   └── research_adapter.py    # Research tools abstraction (SearXNG/AgenticSeek)
├── src/                       # Core source code
│   ├── orchestration/         # Agent orchestration layer
│   │   ├── crew_manager.py    # CrewAI setup and abstraction for swapping frameworks
│   │   └── task_graphs.py     # JSON/YAML definitions for task flows (planner outputs)
│   ├── agents/                # Individual agent implementations
│   │   ├── planner_agent.py   # Plans research tasks
│   │   ├── research_agent.py  # Gathers data (web/API/browser)
│   │   ├── intelligence_agent.py # Summarizes/structures findings
│   │   ├── knowledge_agent.py # Writes to/looks up documentation
│   │   └── retrieval_agent.py # Hybrid search from vector DB
│   ├── tools/                 # Custom tools for agents
│   │   ├── web_search_tool.py # SearXNG integration
│   │   ├── browser_tool.py    # AgenticSeek integration
│   │   ├── api_tool.py        # Generic API hitter (e.g., arXiv)
│   │   └── hybrid_search_tool.py # Qdrant hybrid query
│   └── utils/                 # Helpers
│       ├── embedding_utils.py # Open embedding models (e.g., SentenceTransformers)
│       └── logging_utils.py   # Basic logging (pre-monitoring)
├── data/                      # Local data stores (for prototyping)
│   ├── artifacts/             # Raw research outputs (JSON/HTML/PDF snapshots)
│   └── embeddings/            # Temp storage if needed (Qdrant handles persistence)
├── docker/                    # Dockerfiles/Compose (deferred)
│   ├── Dockerfile             # Base image for app
│   └── docker-compose.yml     # Services: app, Ollama, Qdrant, Outline, SearXNG
├── tests/                     # Unit/integration tests
│   └── test_agents.py         # Dry-run agent flows
└── scripts/                   # Setup/run scripts
    ├── setup_local.sh         # Install deps, start services
    └── run_prototype.sh       # End-to-end local run
```

## Detailed Plan for Each Component

### 1. Agent Orchestration (CrewAI Initial)

- **Role**: Coordinates multi-agent communication autonomously. Uses role-based "crews" for tasks like planning → research → synthesis → update. Abstraction layer (in `config/agents.yaml` and
  `src/orchestration/crew_manager.py`) normalizes contracts (e.g., start/stop, messages, tools) for swapping to LangGraph/AutoGen.
- **Pros/Cons from Responses**: Pros: Lightweight, autonomy-focused (CrewAI); flexible graphs (LangGraph alternative). Cons: Opinionated (CrewAI); more engineering for swaps.
- **Integration**: Agents communicate via JSON messages/task graphs. Store state in local JSON/Redis (for small teams). Support spawning niche research sub-agents (e.g., for academic papers) dynamically based on planner
  output.
- **Format**: Task graphs as JSON (e.g., `{task_id, query, sources, tools[]}`).
- **Agnosticism**: Adapter handles framework swaps without rewriting agent logic.

### 2. Planner Agent

- **Role**: Autonomous decomposition of high-level queries into task graphs. Outputs plans for research (e.g., sources: blogs/APIs/papers), priorities, and tool selection. Spawns sub-agents for niches (e.g., technical
  vs. academic).
- **Pros/Cons from Responses**: Pros: Hierarchical decomposition (LangGraph-style); event-driven (AutoGen alternative). Cons: Over-planning in simple cases.
- **Integration**: Uses LLM (Llama 3.2 11B) via adapter. Inputs: user/system prompts. Outputs: JSON task graphs to queue (e.g., local file/Redis). Autonomous: No human input needed; retries on invalid plans.
- **Format**: JSON graphs (e.g., `{query, subtasks[], deadlines, niches[]}`).
- **Agnosticism**: LLM adapter for swaps; task graphs neutral for any orchestrator.

### 3. Research Agent

- **Role**: Autonomous data gathering. Performs web searches (SearXNG), browser automation (AgenticSeek for dynamic sites), API hits (e.g., arXiv). Spawns sub-agents for niches (e.g., paper parsing with Grobid).
- **Pros/Cons from Responses**: Pros: Privacy (SearXNG); robust JS handling (Playwright alternatives like AgenticSeek). Cons: Resource use in browsers; coverage limits in metasearch.
- **Integration**: Tools via adapter (e.g., `tools/web_search_tool.py`). Outputs: Artifacts as JSON (e.g., `{url, timestamp, raw_text, metadata}`) stored in `data/artifacts/`. Autonomous: Selects tools based on plan;
  handles retries/failovers.
- **Format**: JSON artifacts; snapshots as HTML/PDF.
- **Agnosticism**: Adapter for tool swaps (e.g., to Firecrawl/Skyvern); API/browser hybrid by default.

### 4. Intelligence Agent

- **Role**: Autonomous summarization/structuring of research artifacts. Uses LLM to extract summaries, tags, citations; proposes doc placements/revisions.
- **Pros/Cons from Responses**: Pros: Multi-pass summarization (Haystack/LlamaIndex influences); high-quality open models. Cons: GPU needs for larger models.
- **Integration**: Inputs: JSON artifacts. Outputs: Structured JSON + Markdown (e.g., `{title, summary_md, tags[], citations[]}`). Uses embedding utils for semantic tags.
- **Format**: JSON + Markdown; templates for consistency.
- **Agnosticism**: LLM adapter (initial: Llama 3.2 11B); wrap in chains for swaps.

### 5. Knowledge Agent

- **Role**: Autonomous writes/lookups in documentation platform. Updates via API; versions at document level. Serves as source for RAG.
- **Pros/Cons from Responses**: Pros: Collaborative GUI (Outline); structured linking/diagrams. Cons: DB setup (PostgreSQL for Outline).
- **Integration**: Uses adapter to Outline API. Inputs: Intelligence outputs. Outputs: Updated docs with metadata (e.g., provenance). Autonomous: Checks for existing docs; handles conflicts.
- **Format**: Markdown for body; JSON sidecar for metadata (e.g., embeddings, versions).
- **Agnosticism**: Adapter for swaps (e.g., to BookStack/Wiki.js); neutral formats.

### 6. Documentation Tool (Outline Initial)

- **Role**: Self-hosted GUI for human/machine edits. Stores text/diagrams (Mermaid embeds); structured links via Markdown/slugs. Becomes RAG source.
- **Pros/Cons from Responses**: Pros: Real-time edits, versioning; API access. Cons: Redis/DB needs.
- **Integration**: REST API for agents; GUI for humans. Chunk docs for embeddings.
- **Format**: Markdown with YAML frontmatter for metadata.
- **Agnosticism**: Adapter handles API differences.

### 7. Retrieval Agent

- **Role**: Hybrid search (semantic + keyword) from vector DB. Assembles contexts for RAG queries.
- **Pros/Cons from Responses**: Pros: Fast filtering (Qdrant); hybrid for accuracy. Cons: Index management.
- **Integration**: Uses Qdrant client via adapter. Inputs: Queries. Outputs: Ranked snippets with provenance. Autonomous: Reranks with small LLM if needed.
- **Format**: JSON results (e.g., `{snippet, score, doc_id, version}`).
- **Agnosticism**: Adapter for DB swaps (e.g., to Weaviate/Chroma).

## Recommended Sequence of Implementation Steps

Focus on local end-to-end prototype. Run on a single machine with Ollama/Qdrant/Outline/SearXNG installed locally. Use virtualenv for Python.

1. **Get AI Orchestrator Running**: Set up CrewAI with abstraction. Define a simple crew in `src/orchestration/`. Test with mock agents/tools via `scripts/run_prototype.sh`.
2. **Implement Planner Agent**: Add to `src/agents/`. Use LLM adapter. Test planning a sample query into JSON graph.
3. **Implement Research Agent**: Integrate tools via adapter. Test web/API gathering; store artifacts.
4. **Implement Intelligence Agent**: Add summarization logic. Test on mock artifacts; output structured JSON/Markdown.
5. **Set Up Documentation Platform**: Install Outline locally (PostgreSQL/Redis). Configure adapter.
6. **Implement Knowledge Agent**: Connect to Outline API. Test writing/updating from intelligence outputs.
7. **Implement Retrieval Agent**: Install Qdrant locally. Add embedding/indexing on doc updates. Test hybrid queries.
8. **End-to-End Integration**: Wire full flow in orchestrator. Run prototype: query → plan → research → intelligence → knowledge → retrieval.
9. **Add Agnosticism and Autonomy**: Refine adapters; ensure agents handle failures autonomously.
10. **Defer: Infrastructure/Monitoring**: Containerize with Docker Compose; add Kubernetes manifests. Integrate Grafana/Prometheus for metrics.
