Great — let’s jump in. Below is a focused, practical architecture + toolset survey for a **self-updating, fully open-source RAG knowledge base** that meets your constraints: agent-framework agnostic, LLM-agnostic,
vector-DB agnostic, fully self-hostable, document-level versioning (not Git), browser + API search, and multi-agent orchestration. I give multiple options for each component, formats each component expects, pros/cons,
and an overall recommended stack tuned for a small, scalable team.

> Quick note: I looked up the primary OSS projects to ensure recommendations reflect current, production-ready projects (agent frameworks, vector DBs, doc platforms, LLMs). Key references used for core claims:
> LangGraph (agent orchestration), CrewAI (agent framework alternative), Qdrant (vector DB), Wiki.js (self-hosted doc platform), and Mistral (open LLM family). ([GitHub][1])

---

# 1) High-level architecture (textual)

Agents ⟷ Planner (coordination) ⟷ Researchers (web/API/browser) ⟷ Intelligence Agent (summarize → docs) ⟷ Knowledge Agent (doc platform, versioned)
Retrieval pipeline: Docs → chunk + embeddings → vector DB (hybrid indexes: vector + keyword) → Retrieval agent → RAG layer → LLM(s).
All components expose well-documented APIs so frameworks/LLMs/vector DBs/document stores can be swapped without rearchitecting the pipeline.

---

# 2) Agent orchestration — options (framework-agnostic goal)

Goal: multi-agent communication, autonomous agents, swap out frameworks easily.

A. **LangGraph** (low-level orchestration; graph flows)

* Use when you want graph-style flows, explicit state & cycle support, long-running/stateful agent orchestration. Good for planner → multi research agent coordination and complex flows. ([GitHub][1])
* Format/interface: Python/JS libraries, agents talk via APIs or message buses (HTTP/REST, gRPC, or event queues). Store agent metadata as JSON.

B. **CrewAI** (lightweight agent framework focused on autonomy)

* Simpler, highly opinionated for multi-agent “crews” and flows; designed for autonomous agents and production use cases. Good if you prefer a Pythonic library that emphasizes autonomy. ([GitHub][2])
* Format/interface: Python SDK, agents configured with JSON/YAML manifests and HTTP endpoints.

C. **LangChain (or Open Agent Platform)** — as adapter layer

* Not strictly an orchestrator but provides robust tool integrations, wrappers for LLMs, and a de facto standard for composing LLM workflows. Use as a “compatibility” layer so agent logic can be ported between
  frameworks. (LangChain has many tool adapters and patterns.)

Pros & cons summary

* LangGraph: **Pros:** flexible, graph semantics, production usage. **Cons:** more plumbing/engineering to implement tooling.
* CrewAI: **Pros:** quick to build autonomous crews, lightweight. **Cons:** less low-level control for exotic flows.
* LangChain: **Pros:** integration ecosystem; **Cons:** not a first-class multi-agent orchestrator — better used as an integration/compat layer.

**Recommendation:** Use a small abstraction layer (thin adapter) that normalizes **agent contracts** (start/stop, message, tool registry, state snapshot). Implement adapters for 1) LangGraph and 2) CrewAI (or any future
framework). This delivers true framework-agnostic swapping with minimal rewrite.

---

# 3) Planner agent

Role: create research plans, spawn niche research agents, manage tasks (priority/TTL), and accept human prompts.

Options / capabilities

* Planner runs as an agent that outputs **task graphs** (JSON) describing: target query, source types (blog, API doc, academic paper), retrieval priority, time budget, and required toolset (browser/API/scraper).
* Planner should use a **task queue** (Redis/RQ, or RabbitMQ) to schedule research agents; store state in a small relational DB (Postgres) for audit/history.

Why this design

* Task graph JSON is neutral and framework-agnostic, so any orchestrator can interpret it to spawn workers/agents.

Format: planner outputs JSON task graphs and uses HTTP webhooks / message queue to notify research agents.

---

# 4) Research agent (autonomous) — how to gather info

Requirements: support API search + browser automation + scraping + PDFs + papers.

Core tools (open-source):

* **Browser automation:** Playwright (recommended) or Puppeteer / Selenium. Playwright is modern, cross-browser, multi-language. Use headless mode for autonomous scraping and structured extraction. ([Playwright][3])
* **Meta-search proxy:** SearxNG — run your own instance to get aggregated search results without depending on proprietary search APIs. Use SearxNG results as seeds. ([GitHub][4])
* **Academic corpora & large crawls:** Common Crawl + Semantic Scholar exports — for large scale paper ingestion (download + parsing). Use PDF parsers (pdfminer / Grobid) for structure.
* **APIs:** Prefer open, non-proprietary APIs where available. If needed, the research agent can include adapters to commercial search APIs — but you specified only OSS; so default to SearxNG + browser crawling + site
  APIs (e.g., arXiv API).
* **Document parsing:** Tika / Grobid / pdfplumber for PDFs; Readability + boilerplate removal for web pages.

Behavior pattern

* Research agent receives a plan (task graph), selects sources (SearxNG results, curated sites), runs Playwright to render pages, extracts structured content, computes candidate citations (url + snapshot + extracted
  metadata), and returns summarized raw findings and raw artifacts (HTML/PDF snapshot) to the intelligence agent.

Format: extracted artifacts = `{source_url, timestamp, html_snapshot, raw_text, metadata:{title, author, date}, source_type}`. Store snapshot artifacts in object store (S3-compatible MinIO).

Pros/cons:

* Playwright: **Pros:** robust cross-browser automation, modern API. **Cons:** heavier resource usage vs lightweight HTTP scraping.
* SearxNG: **Pros:** privacy, aggregator, self-hosted. **Cons:** can be slower/less comprehensive than large commercial APIs.

---

# 5) Intelligence agent (summarize → docs)

Role: receive raw artifacts from research agents, summarize, structure, and write to documentation platform.

LLM options (LLM-agnostic — pick what fits infra & license):

* **Small / local / fast:** llama.cpp / ggml flows (LLaMA family, GPT-OSS forks) for local inference on CPUs. Great for on-prem demos and privacy. ([GitHub][5])
* **High quality open models:** Mistral (7B family) and Falcon families on Hugging Face — good quality / open weights for on-prem inference where GPUs available. Use these via local inference servers (e.g., text
  generation inference). ([Hugging Face][6])
* **Hybrid strategy:** run smaller models locally for routine summarization, queue long-running expensive summarization to larger hosted local GPU nodes.

Agent behavior & templates

* Intelligence agent uses structured templates: extraction → (1) bullet summary, (2) canonical citation list, (3) semantic tags, (4) suggested doc section placement, (5) revision note (why updated).
* Store output in machine-readable format (JSON+Markdown): `{"id","title","summary_md","embeddings","tags","citations":[{url,title,hash}],"proposed_doc_path"}`.

Format: content written to documentation platform in **Markdown** (or platform native format) plus a parallel machine manifest JSON for structured metadata and versioning.

**LLM switching:** wrap LLM providers behind an inference adapter interface (model_name, context_window, temperature, token_limits). This makes swapping models trivial.

---

# 6) Knowledge agent + Documentation platform (central repo / single source of truth)

Requirements recap: self-hosted GUI, human edits, **document-level versioning (not Git)**, support text + diagrams, structured linking between docs, API for machine updates.

Top OSS options (self-hosted with GUI):
A. **Wiki.js** — modern, modular, Markdown first, revision history per page, REST API, integrates with external auth and storage. Good for structured linking and web editing. ([GitHub][7])

* Format: Markdown (CommonMark with extensions), page metadata as JSON, attachments supported. Revision history built in.

B. **BookStack** — book/chapter/page structure, WYSIWYG + Markdown, page revisions, built-in diagrams.net support for diagrams. Good for book/guide style docs. ([BookStack][8])

C. **Outline** — focused on team knowledge bases, collaborative editor, API for integration, self-hostable community edition. (Has document revisions and a modern UI.) ([GitHub][9])

D. **DokuWiki** — simple, file-based, robust revision history, plugin ecosystem (less modern UI). ([dokuwiki.org][10])

Which to pick?

* If you want **Markdown native + modern UI + strong API** → **Wiki.js**.
* If you want **book-style organization + diagrams.net built-in** → **BookStack**.
* If you want **team KB with collaborative UX** → **Outline**.
* If you want **ultra-simple, file-based** (no DB) → **DokuWiki**.

**Document-level versioning:** all above keep page revisions (i.e., page change history) that are exposed through the UI — this satisfies your “not Git” requirement. Also they provide REST APIs to push programmatic
updates from the Intelligence agent.

Machine format: store the canonical machine manifest (JSON metadata) in the doc page metadata or in a sidecar API table. The doc body itself is Markdown (or HTML) — human editable; metadata contains embeddings and
provenance.

Structured linking & visual media:

* Wiki.js & BookStack support inline attachments, image hosting, embedding diagrams (diagrams.net in BookStack). Use cross-page references (Markdown links + unique slugs). Keep structured metadata (JSON) for graph edges
  to allow traversal (for RAG indexing and graph navigation).

**Recommendation:** for a small team that needs modern UX + API + strong Markdown support => **Wiki.js** (primary) or **BookStack** if diagrams.net + book structure is important.

---

# 7) Vector DB + Retrieval agent (hybrid search)

Goal: hybrid (semantic + keyword) retrieval, vector DB agnostic.

Primary OSS vector DB options

* **Qdrant** — Rust, fast, filterable payloads, supports hybrid search patterns and filtering. Good for real-time updates (streaming). ([Qdrant][11])
* **Weaviate** — schema + vector + hybrid, built-in modules for modular ML models and metadata filtering. Good for richer schema + class definitions. ([docs.weaviate.io][12])
* **Milvus** — highly scalable, K8s native, good for very large indexes and GPU acceleration. ([milvus.io][13])
* **FAISS** (library) — local library for ANN search, great for tightly-controlled, single-node setups (no RPC server unless you wrap it). ([faiss.ai][14])

Hybrid search pattern

* Index per document chunk: `chunk_id, doc_id, text, embedding, metadata (title, tags, url, version, created_at)`
* Use vector similarity to get candidate chunks, then **keyword/metadata filtering and optional BM25 re-ranking** (via SQLite/PG full-text or an inverted index) to combine semantic relevance & exact keyword matching.
  Rerank top N by a small high-quality LLM if necessary.

Retrieval agent responsibilities

* Accept query → run semantic nearest neighbors + metadata filters → run keyword search (if configured) → merge & rerank → return top candidates with provenance (doc id, version, snippet, score, retrieval method).

Vector DB agnostic design

* Provide a `VectorStore` adapter interface in your codebase: `upsert(points)`, `search(vector, filter, top_k)`, `delete(ids)`. Implement adapters for Qdrant, Weaviate, Milvus, and a local FAISS fallback.

Scale guidance

* Small scale (< millions of chunks): Qdrant or Weaviate on single instances is fine.
* Large scale (>100M vectors or heavy concurrency): Milvus or a sharded Qdrant cluster on K8s + GPU workers for embedding generation and reindexing.

---

# 8) Embeddings & chunking (open)

* Use open embedding models (SBERT variants, or small LLM-based embedder) exported via Hugging Face models or custom SentenceTransformers. Keep embeddings as floats of typical dims 512–1536.
* Chunking policy: semantic chunking by sentences/paragraphs, overlap 50–100 tokens; store chunk provenance and source hash.

---

# 9) Formats and data contracts (explicit)

* **Agent task graph**: JSON (fields: `task_id`, `type`, `query`, `sources`, `priority`, `deadline`, `tools[]`)
* **Research artifact**: JSON: `{id, source_url, snapshot_path, raw_text, extracted_metadata, mime_type, timestamp}`
* **Intelligence output**: JSON + Markdown: `{id, title, summary_md, tags[], citations[], proposed_doc_path, embeddings[], provenance[]}`
* **Doc body**: Markdown (primary), with embedded metadata sidecar JSON (or built-in page metadata). Diagrams stored as SVG/diagrams.net JSON attachments.
* **Vector DB entries**: `{vector: [float], payload: {chunk_id, doc_id, snippet, tags, url, version}}`

These neutral formats let you swap agents, vector stores, or documentation platforms.

---

# 10) Deployment & infra (local/private)

You asked to pick a deployment approach — I provide three patterns and pros/cons.

A. **Single-host Docker Compose (recommended for small teams / staging / simple on-prem)**

* Pros: simple, fast to deploy, low infra overhead, reproducible. Easiest for a small team.
* Cons: limited horizontal scaling, single point of failure.

B. **Kubernetes (K8s) on private infra (recommended for production / scale)**

* Pros: scalable, resilient, ideal for auto-scaling vector DB clusters (Milvus), GPU scheduling, rolling updates.
* Cons: operational complexity, need for K8s expertise and a small SRE footprint.

C. **Nomad + Consul (lightweight orchestration) or systemd services (bare metal)**

* Pros: middle ground between Compose and K8s; easier than K8s but more flexible than Compose.
* Cons: smaller ecosystem vs K8s; fewer managed integrations.

Storage & infra recommendations

* **Object store:** MinIO (S3 compatible) for snapshots, PDFs, artifacts.
* **Relational DB:** Postgres for agent state + metadata + doc metadata index.
* **Message queue:** Redis streams or RabbitMQ for task queues.
* **Monitoring:** Prometheus + Grafana + logging stack (Loki/Elastic).
* **Secrets & config:** Vault or sealed secrets for K8s; env files / Hashicorp Vault for on-prem.

If you expect to run heavy LLM inference: co-located GPU nodes (NVIDIA) inside a K8s cluster or dedicated inference servers (Nginx + worker queues) are recommended.

---

# 11) Security & privacy (local)

* Keep everything on private network / VPC.
* Agent actions that fetch web pages should run in sandboxed containers, sanitized file systems, and with strict resource limits.
* Audit logs: every agent action should produce an immutable audit event (source, timestamp, agent_id, action, outcome). Store in Postgres + object store.

---

# 12) Operational patterns (small team)

* Start with **Docker Compose** + **Wiki.js** + **Qdrant** + **Playwright** + local LLM (llama.cpp or Mistral/Falcon on a GPU node). This yields a minimal, maintainable stack that your small team can operate.
* Use **adapter interfaces** for: `AgentAdapter`, `VectorStoreAdapter`, `DocPlatformAdapter`, `LLMAdapter`. Implement two concrete adapters for each to prove swappability (e.g., Qdrant + Weaviate; Wiki.js + BookStack;
  LangGraph + CrewAI).
* CI: use tests that run agent flows in "dry mode", validate outputs and assertions (e.g., artifacts produced, embeddings created, doc created).

---

# 13) Example component mapping (recommended starter stack)

* Orchestration/Adapters: LangGraph (primary), CrewAI (alternate) — adapter layer to normalize contracts. ([GitHub][1])
* Planner Agent: custom microservice producing JSON task graphs; backed by Postgres and Redis queue.
* Research Agent: Playwright + SearxNG seeds + Grobid/Tika for PDFs. ([Playwright][3])
* Intelligence Agent: run local LLMs (Mistral / Falcon / llama.cpp depending on hardware) via a model adapter. ([Hugging Face][6])
* Docs (knowledge source): Wiki.js (Markdown + revisions + API). ([GitHub][7])
* Vector DB: Qdrant (production-ready, payload filters, streaming upserts). ([Qdrant][11])
* Storage/Infra: MinIO for snapshots, Postgres for metadata, Docker Compose for initial deployment, K8s for scale.

---

# 14) Pros/Cons quick table (short form)

Agent Frameworks

* LangGraph — Pros: graph flows, stateful; Cons: more engineering. ([GitHub][1])
* CrewAI — Pros: lightweight, autonomy-first; Cons: opinionated.

Research tooling

* Playwright — Pros: robust rendering; Cons: heavier resource use. ([Playwright][3])
* SearxNG — Pros: OSS meta-search; Cons: coverage depends on upstream engines. ([GitHub][4])

Doc platforms

* Wiki.js — Pros: Markdown native, API, modern; Cons: comparatively new (active dev). ([GitHub][7])
* BookStack — Pros: diagrams, book structure; Cons: less flexible graph linking.

Vector DBs

* Qdrant — Pros: performant, filtering, streaming; Cons: cluster ops at very large scale. ([Qdrant][11])
* Weaviate — Pros: schema + modules; Cons: heavier for small deployments. ([docs.weaviate.io][12])
* Milvus — Pros: extreme scale; Cons: operational complexity. ([milvus.io][13])

LLMs

* llama.cpp / local LLaMA — Pros: local inference, privacy; Cons: model licensing + quality tradeoffs. ([GitHub][5])
* Mistral/Falcon — Pros: high quality open weights; Cons: require GPU for best perf. ([Hugging Face][6])

---

# 15) Roadmap / practical rollout (3 steps for a small team)

1. **Prototype (2–4 weeks):** Docker Compose stack: Wiki.js, Qdrant, Postgres, MinIO, Redis, Playwright worker, a local LLaMA/llama.cpp inference instance. Implement Planner (simple JSON task generator) + one Research
   agent + Intelligence agent (summarize to Wiki.js). Validate end-to-end RAG query.
2. **Harden & Automate (1–2 months):** Add adapters for a second vector DB (Weaviate), add more LLMs (Mistral/Falcon on GPU), add safeties (sandboxing, audit logs), implement hybrid retrieval + reranking.
3. **Scale (ongoing):** Move to K8s for vector DB clustering and GPU scheduling; add observability and autoscaling, implement advanced agent orchestration policies (retry, human approval flows).

---

# 16) Final recommendations (concise)

* Start **small** and **modular**. Build robust adapter interfaces so you can swap LangGraph ↔ CrewAI, Qdrant ↔ Weaviate, Wiki.js ↔ BookStack with minimal code changes.
* Use **Playwright + SearxNG** as the primary research ingestion path to stay fully open-source and avoid proprietary search APIs. ([Playwright][3])
* Use **Wiki.js** (or BookStack if diagrams/book structure required) as the human-facing single source of truth because they provide page revisions and an API for agent writes. ([GitHub][7])
* Use **Qdrant** as your first vector DB for a good balance of speed, features and ease of ops; keep Weaviate or Milvus as scale alternatives. ([Qdrant][11])
* Choose a **hybrid LLM strategy**: local llama.cpp for low-cost privacy tasks; Mistral/Falcon for higher quality when GPU resources are available. ([GitHub][5])

---

# 17) Items I did not include (by choice)

* No proprietary SaaS (e.g., Pinecone, Confluence, OpenAI hosted APIs) per your instruction.
* I did not include code — only formats and data contracts.
* I did not pick a single “golden” LLM; instead I proposed a multi-model strategy and adapter pattern.

---

If you’d like, next I can:

* Produce a **one-page operations checklist** (services, ports, storage, resource estimates).
* Produce **detailed JSON schemas** for the task graph, research artifact, and intelligence output (machine-readable contracts).
* Produce a **plug-and-play adapter spec** for VectorStoreAdapter / DocPlatformAdapter / LLMAdapter so engineers can implement swap-in/out quickly.

Which of those should I produce next?

[1]: https://github.com/langchain-ai/langgraph?utm_source=chatgpt.com "GitHub - langchain-ai/langgraph: Build resilient language agents as graphs."

[2]: https://github.com/crewAIInc/crewAI?utm_source=chatgpt.com "GitHub - crewAIInc/crewAI: Framework for orchestrating role-playing ..."

[3]: https://playwright.dev/?utm_source=chatgpt.com "Fast and reliable end-to-end testing for modern web apps | Playwright"

[4]: https://github.com/searxng/searxng?utm_source=chatgpt.com "GitHub - searxng/searxng: SearXNG is a free internet metasearch engine ..."

[5]: https://github.com/ggml-org/llama.cpp?utm_source=chatgpt.com "GitHub - ggml-org/llama.cpp: LLM inference in C/C++"

[6]: https://huggingface.co/mistralai/Mistral-7B-v0.1?utm_source=chatgpt.com "mistralai/Mistral-7B-v0.1 · Hugging Face"

[7]: https://github.com/Requarks/wiki?utm_source=chatgpt.com "GitHub - requarks/wiki: Wiki.js | A modern and powerful wiki app built ..."

[8]: https://www.bookstackapp.com/docs/user/?utm_source=chatgpt.com "User Documentation - BookStack"

[9]: https://github.com/outline/outline?utm_source=chatgpt.com "GitHub - outline/outline: The fastest knowledge base for growing teams ..."

[10]: https://www.dokuwiki.org/recent_changes?utm_source=chatgpt.com "recent_changes [DokuWiki]"

[11]: https://qdrant.tech/documentation/?utm_source=chatgpt.com "Home - Qdrant"

[12]: https://docs.weaviate.io/weaviate?utm_source=chatgpt.com "Weaviate Database | Weaviate Documentation"

[13]: https://milvus.io/docs?utm_source=chatgpt.com "Milvus vector database documentation"

[14]: https://faiss.ai/?utm_source=chatgpt.com "Welcome to Faiss Documentation"
