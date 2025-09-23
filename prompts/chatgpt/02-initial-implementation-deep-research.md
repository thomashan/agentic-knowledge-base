# Implementation Plan: Self-Updating RAG Knowledge Base System

This plan outlines a step-by-step, local deployment architecture for a Retrieval-Augmented Generation (RAG) knowledge base system. It will use CrewAI for multi-agent orchestration, SearXNG and AgenticSeek for research,
Outline as the documentation platform, Qdrant for the vector database, and Llama 3.2 (11B) as the LLM. All components run in Docker containers (via Docker Compose) on local hardware. The system consists of a *Planner
Agent*, *Research Agent*, *Knowledge Agent*, *Retrieval Agent*, and *Intelligence Agent*, orchestrated by CrewAI. The workflow enables continuous knowledge updates from web sources. The following sections describe each
component, the directory layout, and an ordered implementation sequence.

## Project Directory Structure

Organize code and data into a clear hierarchy. For example:

```
project-root/  
├── crew/ # CrewAI configurations and workflows  
│ ├── crew_config.yaml # Define agents (planner, research, etc.)  
│ └── flows/ # CrewAI flows/process definitions  
├── agents/ # Custom agent code and utilities  
│ ├── planner_agent/  
│ ├── research_agent/  
│ ├── knowledge_agent/  
│ ├── retrieval_agent/  
│ └── intelligence_agent/  
├── data/  
│ ├── outline/ # Outline knowledge base data (e.g., SQLite/Postgres files)  
│ ├── qdrant/ # Qdrant data directory for vector store  
│ └── raw/ # Raw scraped data and documents  
├── docker/ # Docker Compose and related configs  
│ └── docker-compose.yml # Defines containers for CrewAI, SearXNG, Outline, Qdrant, etc.  
├── models/ # Local LLM weights (e.g., Llama 3.2 11B)  
└── README.md # High-level documentation and setup instructions
```

This structure cleanly separates orchestration (crew/), agent code (agents/), data storage (data/), and deployment (docker/).

## Infrastructure and Deployment

**Docker Compose**: Use Docker Compose to define and run all services locally. Key containers include:

* **CrewAI / Agent Executor**: A Python-based service running the CrewAI framework and all custom agents. This container includes the Llama 3.2 model and Python environment.

* **SearXNG Search API**: A self-hosted SearXNG instance (could use the official SearXNG image) providing a RESTful search API. SearXNG is a privacy-respecting meta-search engine that aggregates results from many
  sources[[1]](https://github.com/searxng/searxng#:~:text=SearXNG%20is%20a%20free%20internet,are%20neither%20tracked%20nor%20profiled).

* **AgenticSeek**: AgenticSeek runs inside the CrewAI container (or a sidecar) to autonomously browse and scrape web content.

* **Outline Knowledge Base**: A container (typically Node.js plus a database) running Outline (an open-source team wiki) for storing and editing collected
  knowledge[[2]](https://www.getoutline.com/#:~:text=Open%20source). Outline should be configured with a persistent database (e.g. Postgres) stored under data/outline/.

* **Qdrant Vector DB**: A container running Qdrant (a Rust-based vector database) to store embeddings and perform similarity
  search[[3]](https://qdrant.tech/documentation/#:~:text=Qdrant%20is%20an%20AI,meaningful%20information%20from%20unstructured%20data). Persist Qdrant data in data/qdrant/.

* **Llama 3.2 Model**: The LLM weights for Llama 3.2 11B reside on the host (in models/) and are mounted into the CrewAI container for local inference.

No Kubernetes or cloud services are used; everything is local. This setup ensures complete control and privacy.

## CrewAI Orchestration Framework

**Install & Configure CrewAI**: In the CrewAI container, install CrewAI (a Python multi-agent orchestration framework) and its dependencies. CrewAI allows defining *crews* of agents with roles, tools, memory, and
knowledge[[4]](https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19#:~:text=What%20is%20Crew%20AI%20%3F)[[5]](https://docs.crewai.com/#:~:text=RAG%20%26%20Vector%20Stores%20Provider%E2%80%91neutral,37%204%20Enterprise%20Deploy).

**Define a Crew and Flows**: Create a crew_config.yaml (or Python script) to define each agent (planner, research, knowledge, retrieval, intelligence), their initial roles, goals, and available tools. Specify multi-step
*flows* (processes) that coordinate agents’ interactions. For example, a workflow might break a query into subtasks, delegate them to agents, and gather
results[[6]](https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19#:~:text=,down%20into%20smaller%2C%20more%20manageable). Use CrewAI’s concepts of Tasks and Processes to
outline how agents communicate.

CrewAI supports built-in RAG and vector store integration. The documentation notes: *“RAG & Vector Stores: Provider-neutral client. ChromaDB by default, Qdrant
supported”*[[5]](https://docs.crewai.com/#:~:text=RAG%20%26%20Vector%20Stores%20Provider%E2%80%91neutral,37%204%20Enterprise%20Deploy). Configure CrewAI to use Qdrant for vector storage. Also enable CrewAI’s
memory/knowledge features for short- and long-term memory[[7]](https://docs.crewai.com/#:~:text=outputs%20with%20Pydantic,23).

## Planner Agent

The **Planner Agent** is responsible for high-level task decomposition and scheduling. In the crew configuration, the planner acts as the central coordinator:

* **Task Definition**: When a user query or update goal arrives, the planner breaks it into subtasks. For a user query, tasks might be: “Run retrieval for relevant docs” and then “Generate answer.” For knowledge updates,
  tasks might be: “Identify new topics to search” and then “trigger research agent.”

* **Crew Leadership**: The planner assigns tasks to other agents based on their specialties (e.g. research tasks to the Research Agent). CrewAI lets you assign tasks to specific agents or distribute
  them[[6]](https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19#:~:text=,down%20into%20smaller%2C%20more%20manageable).

* **Flow Control**: Complex tasks may involve sequential or parallel processes. Use CrewAI Flows to represent these multi-step procedures. For example, a “Weekly Update” flow could tell the Research Agent to gather news
  on predefined topics, then hand off to the Knowledge Agent.

Initially, implement the planner logic in the CrewAI config (YAML or Python). Later, refine by adding memory/logging so the planner can avoid repeating work.

## Research Agent (Web Search & Crawling)

The **Research Agent** gathers new information from the web. It uses two tools:

* **SearXNG Search**: When given a topic or query, the agent calls the SearXNG API (e.g. GET /search?q=...&format=json) to retrieve search results. SearXNG is an open-source metasearch engine that aggregates results
  from hundreds of sources and doesn’t track users[[1]](https://github.com/searxng/searxng#:~:text=SearXNG%20is%20a%20free%20internet,are%20neither%20tracked%20nor%20profiled). This provides fresh URLs relevant to the
  query.

* **AgenticSeek Crawler**: For each promising result, the agent invokes AgenticSeek to browse and scrape content. AgenticSeek is a local-first autonomous agent that can *“autonomously browse the internet, search, read,
  extract information, and fill out web forms”*[[8]](https://research.aimultiple.com/open-source-web-agents/#:~:text=,hosted). It can retrieve page text, handle navigation, and extract relevant sections.

**Workflow**: The Research Agent takes inputs (topics or queries) from the Planner Agent. It first queries SearXNG to get a list of result links. Then, it feeds those links into AgenticSeek. AgenticSeek visits each URL,
extracts the textual content (e.g. article text), and returns it to the Research Agent.

The Research Agent then passes the raw text (or selected excerpts) to the Knowledge Agent for storage and indexing.

## Knowledge Agent (Outline Documentation)

The **Knowledge Agent** manages storing and organizing information in the knowledge base:

* **Outline Integration**: Outline is a collaborative wiki for team documentation[[2]](https://www.getoutline.com/#:~:text=Open%20source). The agent uses Outline’s API (Outline has an open API) to create or update
  documents. For example, for each new article or topic discovered, the agent can create a new page in Outline or append to an existing page. This ensures the knowledge base is human-readable and editable. Outline’s
  full-text search and real-time editing features provide a great interface for users[[9]](https://www.getoutline.com/#:~:text=Image)[[2]](https://www.getoutline.com/#:~:text=Open%20source).

* **Content Curation**: The Knowledge Agent may preprocess text (summarization, formatting) before saving. It can tag pages or organize them into hierarchies relevant to queries.

* **Embedding and Indexing**: Crucially, the agent also generates vector embeddings of the content for retrieval. Using an embedding model (it could use Llama itself or a smaller embedding model), each document or
  paragraph is converted to a numeric vector. These vectors are inserted into Qdrant (the vector DB). Outline’s stored content links to these embeddings via metadata. CrewAI’s built-in knowledge feature supports vector
  stores, and Qdrant integration is explicitly supported[[5]](https://docs.crewai.com/#:~:text=RAG%20%26%20Vector%20Stores%20Provider%E2%80%91neutral,37%204%20Enterprise%20Deploy).

After processing, the knowledge base (Outline) now contains the new information in structured form, and the vector DB is updated.

## Retrieval Agent (Qdrant Vector Database)

The **Retrieval Agent** handles queries against the knowledge base:

* **Query Embedding**: When a user or the planner asks a question, the Retrieval Agent first converts the query into an embedding (using the same model as for documents).

* **Vector Search**: It then queries Qdrant to find the most similar document embeddings. Qdrant is an *“AI-native vector database and semantic search
  engine”*[[3]](https://qdrant.tech/documentation/#:~:text=Qdrant%20is%20an%20AI,meaningful%20information%20from%20unstructured%20data) designed for scalable similarity search. Qdrant returns the top-N most relevant
  document IDs or content snippets.

* **Context Assembly**: The agent retrieves the corresponding text from Outline (via ID mapping or stored payload in Qdrant) and packages these as context.

This agent effectively provides RAG’s retrieval step. (By design, RAG has an *information retrieval component* that uses the user query to *pull information from new data sources* and then augments the prompt with
it[[10]](https://aws.amazon.com/what-is/retrieval-augmented-generation/#:~:text=Without%20RAG%2C%20the%20LLM%20takes,provide%20an%20overview%20of%20the).)

## Intelligence Agent (Llama 3.2 LLM)

The **Intelligence Agent** is the LLM-powered component that generates final answers:

* **Language Model Setup**: Use Llama 3.2 with 11 billion parameters (Vision model) running locally. According to Meta’s release, Llama 3.2 includes an 11B model (with vision capabilities) optimized for reasoning and
  question-answering[[11]](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision#:~:text=The%20Llama%203.2,for%20visual%20recognition%2C%20image%20reasoning). We assume a text-only use here, but the model is capable
  of handling long contexts.

* **Prompting with Context**: The agent receives the user query plus the retrieved context from the Retrieval Agent. It formats a prompt incorporating the question and relevant document excerpts.

* **Answer Generation**: The Llama 3.2 model (hosted locally in the CrewAI container) processes the augmented prompt and generates an answer. This output can include citations to the source documents if desired (to
  increase trust[[12]](https://aws.amazon.com/what-is/retrieval-augmented-generation/#:~:text=Enhanced%20user%20trust)).

* **Response**: The final answer is returned to the user or calling system via the CrewAI framework.

In summary, the Intelligence Agent completes the RAG cycle: it uses retrieved knowledge to produce an up-to-date, accurate response. Because Llama 3.2 is run locally, there is no external API call, keeping data in-house.

## Integration Workflow

The **end-to-end workflow** ties all components together in CrewAI:

1. **Initialization**: Deploy all containers via Docker Compose. Ensure SearXNG, Outline, and Qdrant are running and accessible. Start the CrewAI service.

2. **Kickoff**: A user query or scheduled update triggers the Planner Agent. For a query, the planner creates tasks for retrieval and answering. For an update, the planner might create tasks for exploring web topics.

3. **Research Phase**: If the planner indicates new information is needed, the Research Agent runs (SearXNG → AgenticSeek) and sends output to the Knowledge Agent. The Knowledge Agent writes to Outline and updates Qdrant
   embeddings.

4. **Retrieval Phase**: For a query, the Retrieval Agent takes the query, finds relevant documents in Qdrant, and retrieves those texts from Outline.

5. **Answer Phase**: The Intelligence Agent (Llama) takes the query + context and generates an answer.

6. **Iterate**: The system can loop—e.g., the answer might spark follow-up questions, or the planner may schedule periodic re-search for topic freshness.

CrewAI orchestrates this flow, passing messages between agents and managing the process state. With this setup, the system continuously learns: when new web content appears, the Research and Knowledge agents ingest it,
and the vector index updates, making future answers more accurate.

## Self-Updating Mechanism

To keep the knowledge base **self-updating**, implement scheduled or trigger-driven updates:

* **Periodic Crawls**: The Planner Agent can have a daily or weekly task to invoke the Research Agent on key topics or news sites. For example, “Search the latest articles about [domain]” and ingest them.

* **Event-driven Updates**: If users ask about recent events, the Planner can detect “I don’t know” from LLM output or low similarity scores, then schedule a targeted research task.

* **Change Detection**: Optionally, track timestamps of Outline articles and re-crawl sources if they’ve been updated.

* **Automation Tools**: CrewAI can integrate job schedules or cron-like processes in flows. Alternatively, a simple loop in the Planner agent’s code can check for update conditions.

This ensures that the system doesn’t rely solely on static training data: new facts from the web are continuously pulled in, embedded, and made available to the LLM.

## Monitoring and Observability

As a final step, add monitoring to track system health:

* **Prometheus & Grafana**: Instrument the CrewAI service and agents to expose metrics (e.g., query counts, response times, embedding errors). Use Prometheus to scrape these metrics and Grafana to visualize them.

* **Logging**: Capture logs from each container. Outline and Qdrant have their own logs; CrewAI can log agent interactions.

* **Health Checks**: Ensure containers expose health endpoints (Docker Compose can use healthcheck).

* **CrewAI Built-in Telemetry**: CrewAI’s documentation mentions built-in observability integrations (tracing, metrics) and potential LangChain-like
  monitoring[[5]](https://docs.crewai.com/#:~:text=RAG%20%26%20Vector%20Stores%20Provider%E2%80%91neutral,37%204%20Enterprise%20Deploy). Configure any recommended telemetry.

Monitoring is not required for initial functionality, but it provides insights and alerting once the system is running.

## References

* CrewAI framework with multi-agent orchestration, built-in memory/knowledge, and vector store
  support[[4]](https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19#:~:text=What%20is%20Crew%20AI%20%3F)[[5]](https://docs.crewai.com/#:~:text=RAG%20%26%20Vector%20Stores%20Provider%E2%80%91neutral,37%204%20Enterprise%20Deploy).

* Retrieval-Augmented Generation (RAG) principles: augmenting LLMs with external knowledge via
  retrieval[[13]](https://aws.amazon.com/what-is/retrieval-augmented-generation/#:~:text=Retrieval,and%20useful%20in%20various%20contexts)[[10]](https://aws.amazon.com/what-is/retrieval-augmented-generation/#:~:text=Without%20RAG%2C%20the%20LLM%20takes,provide%20an%20overview%20of%20the).

* SearXNG meta-search engine (open-source, privacy-focused) for web search[[1]](https://github.com/searxng/searxng#:~:text=SearXNG%20is%20a%20free%20internet,are%20neither%20tracked%20nor%20profiled).

* AgenticSeek autonomous web agent for browsing and data extraction[[8]](https://research.aimultiple.com/open-source-web-agents/#:~:text=,hosted).

* Outline knowledge base platform (open-source, self-hostable wiki)[[2]](https://www.getoutline.com/#:~:text=Open%20source).

* Qdrant vector database for embedding storage and semantic search[[3]](https://qdrant.tech/documentation/#:~:text=Qdrant%20is%20an%20AI,meaningful%20information%20from%20unstructured%20data).

* Llama 3.2 (11B) language model, Meta’s local LLM for inference[[11]](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision#:~:text=The%20Llama%203.2,for%20visual%20recognition%2C%20image%20reasoning).

These technologies together enable the proposed self-updating RAG system. The plan above structures their integration from ground up, ensuring each component is correctly deployed, connected, and sequenced.

---

[[1]](https://github.com/searxng/searxng#:~:text=SearXNG%20is%20a%20free%20internet,are%20neither%20tracked%20nor%20profiled) GitHub - searxng/searxng: SearXNG is a free internet metasearch engine which aggregates
results from various search services and databases. Users are neither tracked nor profiled.

[https://github.com/searxng/searxng](https://github.com/searxng/searxng)

[[2]](https://www.getoutline.com/#:~:text=Open%20source) [[9]](https://www.getoutline.com/#:~:text=Image) Outline – Team knowledge base & wiki

[https://www.getoutline.com/](https://www.getoutline.com/)

[[3]](https://qdrant.tech/documentation/#:~:text=Qdrant%20is%20an%20AI,meaningful%20information%20from%20unstructured%20data) Home - Qdrant

[https://qdrant.tech/documentation/](https://qdrant.tech/documentation/)

[[4]](https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19#:~:text=What%20is%20Crew%20AI%20%3F) [[6]](https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19#:~:text=,down%20into%20smaller%2C%20more%20manageable)
CrewAI: Orchestrating Powerful Collaborative AI Agents | by Anoop Maurya | Medium

[https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19](https://medium.com/@mauryaanoop3/crewai-orchestrating-powerful-collaborative-ai-agents-15408d0bcb19)

[[5]](https://docs.crewai.com/#:~:text=RAG%20%26%20Vector%20Stores%20Provider%E2%80%91neutral,37%204%20Enterprise%20Deploy) [[7]](https://docs.crewai.com/#:~:text=outputs%20with%20Pydantic,23) CrewAI Documentation -
CrewAI

[https://docs.crewai.com/](https://docs.crewai.com/)

[[8]](https://research.aimultiple.com/open-source-web-agents/#:~:text=,hosted) Best 30+ Open Source Web Agents

[https://research.aimultiple.com/open-source-web-agents/](https://research.aimultiple.com/open-source-web-agents/)

[[10]](https://aws.amazon.com/what-is/retrieval-augmented-generation/#:~:text=Without%20RAG%2C%20the%20LLM%20takes,provide%20an%20overview%20of%20the) [[12]](https://aws.amazon.com/what-is/retrieval-augmented-generation/#:~:text=Enhanced%20user%20trust) [[13]](https://aws.amazon.com/what-is/retrieval-augmented-generation/#:~:text=Retrieval,and%20useful%20in%20various%20contexts)
What is RAG? - Retrieval-Augmented Generation AI Explained - AWS

[https://aws.amazon.com/what-is/retrieval-augmented-generation/](https://aws.amazon.com/what-is/retrieval-augmented-generation/)

[[11]](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision#:~:text=The%20Llama%203.2,for%20visual%20recognition%2C%20image%20reasoning) meta-llama/Llama-3.2-11B-Vision · Hugging Face

[https://huggingface.co/meta-llama/Llama-3.2-11B-Vision](https://huggingface.co/meta-llama/Llama-3.2-11B-Vision)
