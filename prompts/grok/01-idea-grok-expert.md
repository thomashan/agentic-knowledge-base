### Agent Framework

The agent framework handles orchestration for multi-agent systems, ensuring autonomy (e.g., agents can self-direct tasks without manual intervention) and abstraction for easy switching. Focus on open-source options
supporting multi-agent communication like message passing or graphs, as per your preference for LangGraph or CrewAI. All options are Python-based for broad compatibility, but abstraction layers (e.g., via adapters) allow
language switches.

| Option    | Description                                                                                                                                                 | Pros                                                                                                                                             | Cons                                                                                           |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| CrewAI    | Role-based orchestration framework for defining autonomous agents with tasks, delegation, and collaboration. Supports spinning up niche agents dynamically. | Easy to set up roles for planner/research/intelligence; strong community for extensions; lightweight for small teams.                            | Less flexible for complex stateful workflows compared to graph-based tools.                    |
| LangGraph | Graph-based extension of LangChain for building stateful, multi-agent workflows with cycles and conditional routing.                                        | Highly abstract and modular (easy to swap components); excellent for autonomous planning and research loops; integrates well with RAG pipelines. | Steeper learning curve for graph modeling; requires LangChain familiarity.                     |
| AutoGen   | Microsoft-backed framework for conversational multi-agent systems, enabling agents to interact via messages and tools.                                      | Built-in autonomy for delegation (e.g., research to niche sub-agents); supports human-in-loop for doc reviews; scalable for small teams.         | Heavier dependency on Microsoft ecosystem; conversation focus may overcomplicate simple tasks. |

**Recommendation**: Start with CrewAI for its simplicity in role-based autonomy, ideal for small teams spinning up niche research agents. Abstract via a config layer (e.g., YAML for agent defs) to switch frameworks
without code changes.

### Planner Agent

The planner agent uses the chosen framework to outline research strategies, breaking down topics (e.g., technical blogs vs. academic papers) into autonomous sub-tasks. It leverages LLMs for reasoning and can dynamically
spin up research agents.

- Integrated into the framework above (no separate tool needed).
- Options mirror the framework: Use CrewAI's hierarchical planning or LangGraph's node-based decomposition.
- **Pros (general)**: Enables self-updating by periodically re-planning based on doc gaps; autonomous via LLM prompting.
- **Cons (general)**: Relies on LLM quality for accurate plans; may over-plan for simple queries.

**Recommendation**: Embed planning logic in LangGraph for graph-based adaptability, allowing niche agents (e.g., one for API docs) to be invoked conditionally.

### Research Agent

Autonomous agents for gathering data from web searches (API-based for speed, browser for dynamic sites), APIs (e.g., arXiv for papers), and blogs/docs. Framework-agnostic via tool wrappers. Use open-source libs:
duckduckgo-search for API web search (no key needed), Playwright/Selenium for browser driving, and requests/httpx for APIs. Spin up niche variants (e.g., arXiv-specific) as sub-agents.

| Option                                    | Description                                                                                                              | Pros                                                                                                                                                  | Cons                                                                                              |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| Playwright + duckduckgo-search + requests | Browser automation (Playwright) paired with API search (duckduckgo-search) and HTTP client (requests) for full coverage. | Versatile (handles JS-heavy sites via browser, fast APIs for search/papers); fully local/open-source; easy to abstract for framework swaps.           | Browser driving is resource-intensive; search lib may hit rate limits on heavy use.               |
| LaVague                                   | LLM-driven web navigation library for autonomous browsing and scraping.                                                  | Semantic understanding for targeted research (e.g., "find latest on RAG in papers"); integrates browser/API seamlessly; lightweight for niche agents. | Early-stage (less mature docs); focused on web, needs pairing for pure APIs.                      |
| Browser-Use                               | Tool for AI agents to control browsers programmatically, with scraping and form-filling.                                 | High autonomy (natural lang commands for research tasks); extensible for API hits; runs locally.                                                      | Setup overhead for MCP server integration; less optimized for non-web sources like academic APIs. |

**Recommendation**: Combine Playwright + duckduckgo-search for hybrid API/browser capability, wrapped in a modular class for easy framework integration. This supports both fast searches and deep dives into dynamic
content like blogs.

### Intelligence Agent

Handles summarization, structuring (e.g., extracting entities/links), and writing to the doc platform. LLM-agnostic via wrappers like LiteLLM, which proxies any open inference engine.

| Option                          | Description                                                                                            | Pros                                                                                                                 | Cons                                                                      |
|---------------------------------|--------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| Ollama + LiteLLM                | Local LLM runner (Ollama) with agnostic proxy (LiteLLM) for swapping models (e.g., Llama3 to Mistral). | Runs entirely local; supports fine-tuning for domain-specific summarization; easy integration with agent frameworks. | Inference speed varies by hardware; model switching requires restart.     |
| vLLM                            | High-throughput inference engine for batched LLM calls, agnostic via APIs.                             | Efficient for parallel summarizations (e.g., multiple research outputs); GPU-optimized for small-team scaling.       | Primarily GPU-focused (less ideal for CPU-only setups); setup complexity. |
| Text Generation Inference (TGI) | Hugging Face's serving framework for optimized LLM deployment.                                         | Strong for structured outputs (e.g., JSON for doc ingestion); supports quantization for local efficiency.            | Heavier resource use; tied to HF ecosystem for model loading.             |

**Recommendation**: Use Ollama + LiteLLM for its simplicity and true local/agnostic nature, allowing quick swaps between open models like Phi-3 for lightweight tasks.

### Knowledge Agent and Documentation Tool

The knowledge agent interacts with a versioned, self-hosted doc platform as the single source of truth, ingesting structured findings (e.g., via API writes). Platform must support GUI for human edits, doc-level
versioning (revisions, not Git), text/markdown, diagrams (e.g., Mermaid/Draw.io embeds), and structured linking (e.g., wiki-style). Agnostic via API adapters. Format: Primarily Markdown for portability, with YAML
frontmatter for metadata/links.

| Option    | Description                                                                                         | Format                                                    | Pros                                                                                 | Cons                                                          |
|-----------|-----------------------------------------------------------------------------------------------------|-----------------------------------------------------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------|
| BookStack | Simple wiki platform with shelves/books/pages; API for agent writes; revision history per page.     | Markdown + HTML; embeds for diagrams (Mermaid).           | Intuitive GUI for small teams; easy self-hosting; strong linking via internal URLs.  | Limited advanced querying; no native visual media gallery.    |
| Wiki.js   | Modern wiki with Git-backed storage but doc-level revisions; supports modules for diagrams/linking. | Markdown/Git-flavored; Draw.io integration for visuals.   | Highly customizable GUI; robust API for automation; excellent structured navigation. | Steeper setup (Node.js-based); overkill for very basic needs. |
| XWiki     | Enterprise wiki with structured pages, versioning, and extensions for diagrams/links.               | XWiki syntax (Markdown convertible); macro-based visuals. | Advanced linking (e.g., relational DB-like); fully open; GUI for collab.             | Complex for small teams; Java-based (heavier deploy).         |

**Recommendation**: BookStack for its balance of simplicity, GUI ease, and features—ideal for human-AI collab in small teams. Agent writes via REST API in Markdown format, with links as relative paths (
e.g., [[Page|Anchor]]).

### Retrieval Agent

Retrieves from the vector DB for RAG, combining semantic (embeddings) and keyword (BM25/hybrid) search. Agnostic via libraries like Haystack or LlamaIndex. Embeddings from open models (e.g., Sentence Transformers).
Indexes docs from the platform (e.g., via Markdown parsing).

| Option   | Description                                                              | Pros                                                                    | Cons                                                 |
|----------|--------------------------------------------------------------------------|-------------------------------------------------------------------------|------------------------------------------------------|
| Chroma   | Lightweight, embeddable vector DB with hybrid search plugins.            | Simple local setup; fast for small-scale RAG; easy Python integration.  | Less scalable for massive datasets; basic filtering. |
| Weaviate | Cloud-native vector DB with modular hybrid search (semantic + keyword).  | Rich schema for structured docs; GraphQL API for linking; open modules. | Higher resource use; overkill for tiny teams.        |
| Qdrant   | Rust-based vector search engine with payload filtering and hybrid modes. | High performance/local efficiency; strong for keyword-semantic fusion.  | API-focused (less GUI); setup requires Docker.       |

**Recommendation**: Chroma for its embeddability and ease in local RAG pipelines, supporting hybrid search out-of-box for accurate retrieval from Markdown docs.

### Infrastructure

Run everything locally/private for data sovereignty. Use containerization for modularity. Deployment: Docker Compose for simplicity, scaling to Kubernetes for growth.

| Option                                | Description                                                           | Pros                                                                                  | Cons                                                                |
|---------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Docker Compose                        | YAML-defined multi-container orchestration for local/private servers. | Quick setup for all components (agents, DBs, doc platform); portable for small teams. | Limited auto-scaling; manual management for >5 services.            |
| Kubernetes (e.g., Minikube for local) | Container orchestrator for clustered private deploys.                 | Auto-scaling for agent spins/research loads; resilient for 24/7 self-updating.        | High complexity/overhead; not ideal for solo/small teams initially. |

**Recommendation**: Docker Compose on a private VPS or local server—pros outweigh cons for small-team scalability, with easy migration to K8s later.

### Overall Recommendations

For a scalable, self-updating RAG KB in small teams:

- **Stack**: CrewAI (orchestration) + Playwright/duckduckgo-search (research) + Ollama/LiteLLM (intelligence) + BookStack (docs, Markdown format) + Chroma (retrieval) + Docker Compose (infra).
- **Why?** This combo is lightweight, fully local/open-source, and modular—agents autonomously update docs via APIs, humans edit via GUI, RAG pulls hybrid search for precision. Start with periodic cron jobs for
  planning/research cycles; scale by adding niche agents.
- **Scalability Notes**: Handles small teams via role delegation; for growth, abstract APIs ensure swaps (e.g., to Weaviate if data explodes). Total setup: ~1-2 days for PoC, emphasizing autonomy to minimize handholding.
