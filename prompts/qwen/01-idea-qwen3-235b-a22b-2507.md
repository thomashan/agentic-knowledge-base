# Self-Updating Open-Source RAG Knowledge Base Architecture

## Agent Framework Options

### Framework-Agnostic Orchestration

- **LangGraph**: Provides stateful, cyclic agent execution with visual debugging. Highly flexible for complex workflows but requires deeper understanding of state management.
- **CrewAI**: Role-based agent framework with simple task delegation. Easier learning curve but less granular control over agent interactions.
- **NVIDIA NeMo Agent Toolkit**: Open-source framework providing "framework-agnostic profiling, evaluation, and optimization for production AI agent systems." Excellent for production environments but NVIDIA ecosystem
  dependent.

*Recommendation*: Implement a thin abstraction layer over your chosen framework to maintain true framework-agnostic capabilities. CrewAI offers the most straightforward transition path between frameworks.

## Research Agent Implementation

### Web Search Capabilities

- **SearXNG (self-hosted)**: Private, open-source metasearch engine that aggregates results from multiple sources without tracking. Requires maintenance but fully compliant with privacy requirements.
- **Custom scraper with Playwright**: For dynamic content requiring browser automation. More resource-intensive but handles JavaScript-rendered pages effectively.

### Research Agent Architecture

- Design research agents to "maintain up-to-date embeddings and indexes for fast-changing domains" through scheduled refresh cycles.
- Implement "Self-RAG" principles where "knowledge base can be updated simply by changing the document index" rather than retraining models.

## Documentation Platform Options

### Open-Source Knowledge Bases

- **RAGFlow**: "Leading open-source Retrieval-Augmented Generation (RAG) engine that fuses cutting-edge RAG with Agent capabilities" with built-in document management.
- **Outline**: Modern wiki platform with Markdown support, document versioning, and collaborative editing (requires PostgreSQL).
- **BookStack**: Book-like organization with page history/versioning, image embedding, and clean Markdown editor.

*Key Evaluation Criteria*:

- **Versioning**: All options provide document-level versioning (Outline and BookStack use database versioning, RAGFlow has built-in version control)
- **Content Types**: All support text and images; BookStack handles diagrams best through Mermaid.js integration
- **Format**: All primarily use Markdown with WYSIWYG editors

## Intelligence Agent (LLM Processing)

### LLM Agnostic Processing

- Implement a routing layer that can switch between:
    - **Local models via Ollama** (Llama 3, Mistral)
    - **Text-generation-webui** for broader model compatibility
    - **LiteLLM** abstraction layer for consistent API across providers

*Processing Strategy*: Create "strategies and pipelines for efficiently updating and refreshing knowledge bases in RAG systems with new or changed data" through automated summarization workflows.

## Retrieval Agent & Vector Database

### Vector Database Options

- **ChromaDB**: Lightweight, easy to set up, ideal for small teams. Limited scalability but excellent for prototyping.
- **Qdrant**: High-performance, memory-efficient vector search. Better for larger knowledge bases with complex filtering needs.
- **Weaviate**: Combines vector search withGraphQL interface and automatic classification. More resource-intensive but feature-rich.

*Retrieval Strategy*: Implement hybrid search combining "semantic and keywords searching" as required by the user, with configurable weighting between approaches.

## Infrastructure Deployment

### Deployment Options

1. **Docker Compose Setup**
    - *Pros*: Simple deployment, low maintenance, perfect for small teams
    - *Cons*: Limited scalability, no automatic failover

2. **Kubernetes Cluster**
    - *Pros*: Auto-scaling, high availability, resource optimization
    - *Cons*: Steeper learning curve, operational overhead

3. **RAGFlow Self-Contained Deployment**
    - *Pros*: "Fuses cutting-edge RAG with Agent capabilities" in single package
    - *Cons*: Less flexibility in component swapping

## Overall System Recommendation

For a small team prioritizing maintainability while meeting all requirements:

1. **Agent Framework**: CrewAI with a custom abstraction layer for true framework-agnostic operation
2. **Research Agents**:
    - Web search: Self-hosted SearXNG + Playwright for dynamic content
    - API access: Standard HTTP libraries with rate limiting
3. **Intelligence Agent**: LiteLLM abstraction layer routing to local Ollama models
4. **Documentation Platform**: BookStack for its balance of features, simplicity, and robust versioning
5. **Vector Database**: ChromaDB for small teams (switch to Qdrant if scaling becomes necessary)
6. **Deployment**: Docker Compose for initial deployment with migration path to Kubernetes

This architecture creates "a powerful, self-updating knowledge base that provides accurate, context-aware answers to user queries" while remaining fully open-source and self-hosted. The system can "update its knowledge
base simply by changing the document index" without requiring model retraining, making maintenance sustainable.

For research agent specialization, implement a factory pattern where new agent types can be dynamically instantiated based on research domain requirements, creating "an implementation of an Agentic AI framework powered
by a [modular] knowledge base."  This approach ensures true autonomy where agents "do not require handholding to perform any action" as specified in your requirements.
