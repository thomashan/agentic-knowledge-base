# **An Architectural Blueprint for a Self-Updating, Agent-Driven RAG Knowledge Base**

## **Executive Summary**

This report provides a comprehensive architectural blueprint for designing and deploying a self-updating Retrieval-Augmented Generation (RAG) knowledge base system. The architecture is predicated on two core principles:
the exclusive use of open-source, self-hostable technologies to ensure data privacy and control, and the deployment of autonomous AI agents to drive the continuous research, synthesis, and updating of the knowledge
corpus. The proposed system is modular by design, allowing for the substitution of key components to adapt to evolving technological landscapes and specific organizational requirements.

The analysis covers four primary layers of the system architecture:

1. **The Agentic Orchestration Layer:** The central nervous system that manages agent collaboration and workflow execution.
2. **The Autonomous Intelligence and Research Layer:** The tools and agents responsible for external data acquisition from the web.
3. **The Knowledge Base Layer:** The persistent, versioned source of truth that stores curated information.
4. **The RAG Core:** The underlying language models and vector database that power intelligent retrieval.

For each layer, this report evaluates leading open-source options, presenting a comparative analysis of their architectures, capabilities, and trade-offs. The evaluation culminates in a specific, recommended technology
stack and a unified architectural blueprint that illustrates the end-to-end operational flow. The final recommended architecture comprises **LangGraph** for stateful agent orchestration, a hybrid toolkit of **Scrapy**
and **Playwright** for web research, **BookStack** as the API-driven knowledge base, **Qdrant** as the high-performance vector database, and **Llama 3 8B** as the initial, pragmatically self-hostable Large Language
Model (LLM). This blueprint is designed for technical leaders, solutions architects, and senior AI engineers tasked with implementing sophisticated, autonomous AI systems on private infrastructure.

## **I. The Agentic Orchestration Layer: The System's Brain**

The foundation of this autonomous system is the agent orchestration framework. This layer acts as the system's cognitive engine, defining the logic, collaboration patterns, and operational flow of the AI agents. AI agent
frameworks are advanced development platforms that provide the structure and intelligence necessary to build agents capable of reasoning, planning, and executing complex tasks, moving far beyond the capabilities of
simple chatbots.1 The choice of framework is the most critical architectural decision, as it dictates the system's capacity for managing complex, long-running processes, its debuggability, and its overall scalability.

### **A. Framework Deep Dive: Comparative Analysis**

Three prominent open-source frameworks dominate the landscape for multi-agent systems: CrewAI, AutoGen, and LangGraph. Each offers a distinct paradigm for agent collaboration and workflow management.

#### **CrewAI: The Role-Based Collaboration Specialist**

CrewAI is a framework designed to orchestrate role-playing, autonomous AI agents, enabling them to work together to tackle complex goals.2 It operates at a high level of abstraction, allowing developers to focus on
defining agent roles (e.g., "Researcher," "Writer") and specifying their objectives, rather than managing low-level interactions.3 Architecturally, it is a lean, standalone Python framework engineered for speed and
simplicity, independent of other agent frameworks like LangChain.2 It supports two primary modes of operation: autonomous "Crews" for collaborative tasks and event-driven "Flows" for more granular, programmatic control.2

The primary strength of CrewAI lies in its accessibility. It is widely recognized for its low learning curve, comprehensive documentation, and intuitive design, making it an excellent choice for rapid prototyping and
teams new to multi-agent systems.3 Its minimalist architecture translates to high performance and native support for concurrency.3 However, this simplicity can become a constraint for highly intricate, cyclical workflows
that demand more granular state management and error handling.4 Its suitability for compliance-heavy applications may be limited due to a lack of fine-grained validation tools.3

#### **AutoGen: The Conversational Multi-Agent Engine**

Developed by Microsoft, AutoGen is an open-source framework centered on orchestrating multi-agent systems through structured, conversational workflows.1 The core paradigm is that of a "chat room" where specialized AI
agents collaborate, debate, and solve problems together.7 Its architecture is modular and layered, with a Core API managing low-level message passing and a flexible, event-driven runtime.8 The latest versions feature a
redesigned asynchronous architecture that enhances scalability, observability, and cross-language support for Python and.NET.10

AutoGen's key advantage is that it is natively designed for multi-agent collaboration without requiring add-ons.7 It excels in tasks involving code generation and execution, as it has specialized agents and safety
mechanisms (e.g., Docker-based execution) for these purposes.3 The conversational nature of agent interactions makes the system's reasoning process transparent and auditable.6 As a Microsoft-backed project, it benefits
from a large community and robust tool integration capabilities.4 The primary drawback is the increased orchestration overhead; the developer is responsible for manually designing the agent interaction flows and decision
logic.3 Furthermore, its setup can be more involved, and its documentation has been noted for some inconsistencies across versions.4

#### **LangGraph: The State-Driven Workflow Orchestrator**

LangGraph is an extension of the popular LangChain ecosystem, specifically designed for building stateful, multi-agent applications.1 It treats workflows as cyclical graphs, where agents and tools are nodes. This
structure provides explicit and granular control over complex, multi-step processes.3 LangGraph is architected to be a library for creating agent runtimes where state is a first-class citizen, making it exceptionally
well-suited for managing conversational history, memory, and long-running tasks that may involve loops, retries, and human-in-the-loop interventions.7

The principal strength of LangGraph is its unparalleled control over complex workflows, particularly those involving RAG and the coordination of multiple tools.4 Its explicit state management is superior for tracking the
progress of long-running tasks and recovering from failures.4 As part of the LangChain ecosystem, it benefits from a vast library of integrations and deep integration with LangSmith, a powerful platform for observability
and debugging.12 This control comes at the cost of a steeper learning curve, as it requires developers to think in terms of state machines and graph theory.4 For simpler, linear tasks, the framework can feel
unnecessarily complex or over-engineered.3

### **B. Architectural Considerations: Modularity, State, and Autonomy**

The selection of an agent framework presents a fundamental trade-off between developmental simplicity and granular control over operational logic. Frameworks like CrewAI prioritize rapid prototyping through high-level
abstractions 3, while platforms such as LangGraph offer the fine-grained control necessary for complex, stateful processes.5 For a self-updating knowledge base, the core process is inherently long-running, stateful, and
cyclical: research, synthesize, update, verify, and repeat. A simple, role-based abstraction may be insufficient for managing the complexities of this loop, which can involve failed research attempts, content
verification steps, and dynamic re-planning. The system must be able to "remember" what it has researched previously and why an attempt may have failed, which points directly to the need for a state-centric architecture.

LangGraph is explicitly designed for such stateful applications, treating the system's state as a primary component of its graph structure.4 AutoGen manages state through agent memory within a conversational context,
while CrewAI handles it more implicitly through task outputs.4 For a system that must reliably track multi-step research tasks over extended periods, LangGraph's explicit and persistent state management provides a
significant architectural advantage in terms of robustness and debuggability.

### **C. Recommendation for Orchestration**

For the specific use case of building a self-updating RAG knowledge base, **LangGraph** is the recommended orchestration framework. While it presents the steepest learning curve, its core architectural principles align
most closely with the system's requirements. The process of keeping a knowledge base current is not a simple, linear task but a continuous, cyclical workflow that must be resilient to failure and auditable over time.

LangGraph's state-driven, graph-based model provides the necessary control to build this robust, debuggable, and auditable workflow. It allows for the explicit definition of states such as "Planning," "Researching," "
Synthesizing," and "Updating," with conditional logic governing the transitions between them. This makes it straightforward to implement critical features like retries on failed web scrapes, human-in-the-loop
verification steps before publishing content, and complex decision-making based on the outcome of previous steps. Furthermore, its seamless integration with LangSmith for tracing and observability is an invaluable asset
for monitoring and improving the performance of a production-grade autonomous system.4

The following table summarizes the comparative analysis of the three frameworks.

| Feature              | CrewAI                                        | AutoGen                                          | LangGraph                                                  |
|:---------------------|:----------------------------------------------|:-------------------------------------------------|:-----------------------------------------------------------|
| **Core Paradigm**    | Role-based agent collaboration 2              | Conversational, collaborative agent teams 6      | State-driven, cyclical graph-based workflows 12            |
| **State Management** | Implicit, via task outputs 4                  | Managed via agent memory within conversations 4  | Explicit, persistent state object managed by the graph 4   |
| **Ease of Use**      | High; low learning curve, intuitive 3         | Medium; requires manual orchestration design 3   | Low; steep learning curve, requires graph concepts 4       |
| **Best Use Case**    | Rapid prototyping, role-defined tasks 7       | Collaborative problem-solving, code generation 3 | Complex, long-running, stateful applications (e.g., RAG) 5 |
| **Key Weakness**     | Limited control for complex, cyclical logic 4 | Orchestration logic must be manually coded 3     | Can be overly complex for simple tasks 3                   |

## **II. Autonomous Intelligence and Research: The Data Collectors**

Once the orchestration layer is established, the agents require tools to perceive and interact with their primary source of new information: the World Wide Web. This layer comprises the software that enables agents to
browse websites, extract unstructured data, and interact with web elements, effectively acting as their digital senses.13 The choice of tooling in this layer directly determines the quality, accuracy, and breadth of data
the system can acquire.

### **A. Web Interaction and Data Extraction: Scrapy vs. Playwright**

The two leading open-source tools for web data extraction are Scrapy and Playwright, each with a fundamentally different approach and a distinct set of strengths and weaknesses.

#### **Scrapy: The High-Speed Crawling Framework**

Scrapy is an open-source web scraping and crawling framework written in Python. It is engineered for high performance and efficiency, designed to extract structured data from websites at a large scale.14 Its core
operational model is asynchronous; it makes direct HTTP requests to web servers and processes the raw HTML response without rendering the page in a browser.15

Its primary strength is speed. By avoiding the overhead of a browser engine, Scrapy can handle thousands of requests in parallel, making it exceptionally fast and resource-efficient for scraping static websites where all
content is present in the initial HTML document.15 It also comes with a rich, built-in feature set for serious crawling tasks, including automatic link-following, configurable support for proxies and user-agent rotation,
automatic request retries, and data export pipelines to various formats like JSON and CSV.14 However, Scrapy's major limitation is its inability to process content rendered by client-side JavaScript. It struggles with
modern web applications (e.g., those built with React, Angular, or Vue.js) where content is loaded dynamically after the initial page load.14 While workarounds exist, they typically involve integrating Scrapy with a
browser automation tool, which adds significant complexity to the development process.15

#### **Playwright: The Browser Automation Powerhouse**

Playwright is an open-source browser automation framework developed by Microsoft. It is designed not just for scraping but for end-to-end testing of web applications across all modern rendering engines: Chromium (Google
Chrome, Microsoft Edge), Firefox, and WebKit (Apple Safari).15 Unlike Scrapy, Playwright launches and controls a full, headless web browser. It interacts with web pages as a human user would—clicking buttons, filling out
forms, scrolling, and waiting for dynamic content to appear before extracting it.16

Playwright's definitive advantage is its native ability to handle dynamic, JavaScript-heavy websites.14 It is the essential tool for scraping single-page applications (SPAs) and any site that requires user interaction to
reveal content, such as logging in, navigating through menus, or triggering infinite scroll.16 Its API is generally considered more intuitive for developers who are familiar with browser development tools.14 This power
comes at a significant performance cost. Because it must launch a browser, render the full Document Object Model (DOM), and execute all associated scripts, Playwright is substantially slower and more resource-intensive (
CPU and memory) than Scrapy.15 It also lacks the built-in, large-scale crawling infrastructure of Scrapy; logic for tasks like pagination and following links must be implemented manually by the developer.15

### **B. Integrating Research Tools into Agentic Workflows**

An effective autonomous research system must possess the intelligence to dynamically select the most appropriate data extraction tool based on the target website's architecture. This decision-making capability is a
critical planning function for the agentic system, optimizing for both speed and resource consumption. The modern web is a heterogeneous environment of static and dynamic sites, meaning a system relying on a single tool
will either fail to capture critical data (Scrapy-only) or be unacceptably slow and inefficient (Playwright-only).15

Therefore, a hybrid architecture is non-negotiable for achieving robust and efficient autonomy. The agentic workflow, orchestrated by LangGraph, should treat Scrapy and Playwright not as competing alternatives but as
complementary tools within a unified toolkit. The workflow can be designed with distinct nodes for "Static Scraping" and "Dynamic Scraping." An initial, lightweight analysis of a target URL (e.g., a HEAD request or a
check of the raw HTML for JavaScript framework signatures) can determine which path to take. This allows the system to use the fast and low-cost Scrapy tool for the majority of simple web pages, reserving the slower,
more resource-intensive Playwright tool only for the complex, dynamic sites where it is absolutely necessary.

### **C. Recommendation for Research Tooling**

The recommended approach is a **Hybrid Toolkit**, orchestrated by the LangGraph framework, that integrates both **Scrapy** and **Playwright** as distinct, callable tools.

* **Scrapy** should be designated as the default, first-pass tool for all research tasks. Its speed and efficiency make it ideal for high-volume crawling and initial data gathering from static sources.
* **Playwright** should serve as the specialized, "escalation" tool. The agentic workflow should route a task to the Playwright tool only when the initial Scrapy attempt fails to retrieve meaningful content or when the
  agent's plan explicitly requires interaction with web elements (e.g., logging into a source).

This dual-tool strategy provides the optimal balance of speed, capability, and resource efficiency, enabling the autonomous agents to successfully extract information from the widest possible range of web sources. The
following table highlights the key differences that inform this hybrid strategy.

| Feature                      | Scrapy                                          | Playwright                                      | Recommendation                                                                      |
|:-----------------------------|:------------------------------------------------|:------------------------------------------------|:------------------------------------------------------------------------------------|
| **Primary Use Case**         | High-speed, large-scale static site crawling 14 | Dynamic site interaction and data extraction 15 | Use Scrapy for bulk crawling; Playwright for targeted dynamic interaction.          |
| **Performance/Speed**        | Very High (asynchronous HTTP requests) 15       | Low (full browser rendering) 16                 | Default to Scrapy for speed; use Playwright only when necessary.                    |
| **Dynamic Content Handling** | Poor; requires complex integrations 17          | Excellent; native capability 14                 | The primary reason for including Playwright in the toolkit.                         |
| **Scalability**              | Excellent; built for large-scale jobs 16        | Moderate; resource-intensive at scale 16        | Scrapy for breadth, Playwright for depth.                                           |
| **Built-in Crawling**        | Yes (link following, pagination helpers) 14     | No (must be manually coded) 15                  | Leverage Scrapy's crawling for discovery; use Playwright for specific page actions. |
| **Resource Consumption**     | Low (CPU, RAM) 17                               | High (CPU, RAM) 16                              | A key driver for the hybrid approach to manage operational costs.                   |

## **III. The Knowledge Base: The Source of Truth**

The knowledge base is the central repository where the agents store the fruits of their research. It functions as the system's persistent, long-term memory and the single source of truth for the RAG application. The
selection of this component is critical; it must be programmatically accessible for the agents, support versioning to track changes over time, and be capable of storing rich, structured content.

### **A. Platform Analysis: BookStack vs. Docusaurus vs. Wiki.js**

The architectural choice for the knowledge base hinges on its primary method of interaction. Systems designed for programmatic, autonomous updates benefit from a transactional, database-centric model exposed via a REST
API. In contrast, systems built on a "docs-as-code" philosophy are optimized for human developer workflows involving version control and static site generation.18 For this agent-driven system, an API-first,
database-backed platform is architecturally superior.

#### **BookStack: The Opinionated, Database-Driven Wiki**

BookStack is a simple, self-hosted platform for organizing and storing information.19 It is built on the PHP Laravel framework and uses a MySQL database for all content storage.19 Its core organizing principle is an
intuitive, three-tiered hierarchy of Books, Chapters, and Pages.19

BookStack's strengths align remarkably well with the project's requirements. It features a simple user interface with both WYSIWYG and Markdown editors, and notably includes a built-in diagrams.net integration for
creating and embedding rich diagrams directly within pages.19 Most importantly, it provides a mature, built-in REST API that allows for external, programmatic interaction with the knowledge base content.20 It also
features a "page revisions" system, which provides a non-Git, database-backed version history for every page, complete with timestamps and user attribution.19 Its main potential weakness is its rigid hierarchical
structure, which may not be suitable for all types of knowledge organization, though it is well-suited for structured documentation.

#### **Docusaurus: The Developer-Centric Static Site Generator**

Docusaurus is a popular open-source tool for building optimized documentation websites.21 It is built using React and generates static HTML files from content written in MDX (Markdown with JSX components).21 The entire
content and configuration are typically managed as files within a Git repository, embodying the "docs-as-code" paradigm.18

Docusaurus offers an excellent developer experience and produces highly performant websites. Its versioning system is powerful, designed to keep documentation in sync with software project releases by creating complete
snapshots of the documentation for each version.21 However, this Git-based, file-centric model is its critical weakness for this use case. Docusaurus does not have a built-in API for creating or modifying content
programmatically.21 An autonomous agent would need to perform a series of complex and fragile operations—cloning a repository, creating/editing files, committing changes, pushing to a remote, and potentially triggering a
CI/CD pipeline to rebuild and deploy the site. This workflow is entirely misaligned with the need for frequent, transactional updates from an autonomous system.

#### **Wiki.js: The Modern, Extensible Wiki Engine**

Wiki.js is a modern and powerful open-source wiki engine built on Node.js.24 It is highly extensible and flexible, offering compatibility with multiple database backends, including PostgreSQL, MySQL, and SQLite.24 It
supports a variety of content editors and rich content formats, including diagrams and mathematical expressions.24

Like BookStack, Wiki.js is database-driven and features a robust, built-in version tracking system that allows for visual comparison between different page versions.24 It also offers optional Git integration for backup
and synchronization, but this is not the primary storage mechanism, which remains the database.26 This database-centric approach makes it a viable candidate. The primary uncertainty with Wiki.js is the maturity and scope
of its API for programmatic content manipulation. While the platform's design suggests API-first thinking (e.g., a planned "API Docs" editor), the available documentation does not provide clear, comprehensive details on
its current REST API capabilities for creating and updating pages, introducing a degree of implementation risk.24

### **B. Core Requirements Analysis: Versioning, API, and Rich Content**

The entire update loop of the autonomous system depends on the knowledge base's API. A functional, stable API reduces development time and architectural risk for the entire project.

* **API for Programmatic Updates:** BookStack has a well-documented, stable REST API that covers all necessary CRUD (Create, Read, Update, Delete) operations for its content hierarchy.20 This is a confirmed and critical
  capability. Docusaurus lacks this entirely. Wiki.js's API status is not clearly documented, making it a riskier choice.
* **Versioning Method:** The system requires a mechanism to track changes. BookStack's database-backed "page revisions" and Wiki.js's "version tracking" are both perfectly suited for this, as they are granular and don't
  require external processes.19 Docusaurus's file-system-snapshot approach is too heavyweight and cumbersome for frequent, agent-driven updates.23
* **Rich Content Support:** All three platforms offer good support for rich content. BookStack's out-of-the-box integration with diagrams.net is a notable convenience.19

### **C. Recommendation for the Knowledge Base**

The recommended platform for the knowledge base is **BookStack**. It stands out as the only candidate that definitively meets all critical system requirements without ambiguity. It provides a mature and documented REST
API for programmatic updates, a built-in and appropriate non-Git-based versioning system, and excellent support for rich content.19 Its straightforward, database-driven architecture is an ideal foundation for an
application-centric workflow where autonomous agents are the primary content creators. While Wiki.js is a strong contender, the lack of clear API documentation presents an unnecessary risk compared to the proven
capabilities of BookStack.

The following table provides a comparative summary of the knowledge base platforms.

| Feature                             | BookStack                                        | Docusaurus                                                | Wiki.js                                                                   |
|:------------------------------------|:-------------------------------------------------|:----------------------------------------------------------|:--------------------------------------------------------------------------|
| **Core Technology**                 | PHP/Laravel, MySQL 19                            | React, Node.js (Static Site Generator) 21                 | Node.js, various DBs (PostgreSQL, MySQL, etc.) 24                         |
| **Programmatic API (CRUD)**         | **Excellent:** Built-in, documented REST API 20  | **None:** File-based, requires Git \+ build process 21    | **Uncertain:** API exists but lacks clear documentation for content CRUD. |
| **Versioning Method**               | **Excellent:** Database-backed page revisions 19 | **Poor Fit:** File-system snapshots tied to releases 23   | **Excellent:** Database-backed version tracking 24                        |
| **Rich Content (Diagrams)**         | Excellent: Built-in diagrams.net editor 19       | Excellent: Via MDX and custom React components 21         | Excellent: Built-in diagram generation support 24                         |
| **Suitability for Agentic Updates** | **High:** Designed for API-driven interaction.   | **Very Low:** Workflow is complex and fragile for agents. | **Medium:** Architecturally sound, but API uncertainty is a risk.         |

## **IV. The RAG Core: Powering Intelligence and Retrieval**

The RAG core consists of the components that enable the system to understand, process, and retrieve information intelligently. This includes the self-hosted Large Language Models (LLMs) that agents use for summarization
and structuring, and the vector database that stores content embeddings for semantic search.

### **A. Self-Hosted Language Models for Summarization and Structuring**

The agents will leverage LLMs for two crucial transformation tasks: summarizing large volumes of scraped web content into concise knowledge and structuring this information into a consistent format (e.g., JSON) for
storage in the knowledge base.30

#### **Model Options and Analysis**

The open-source LLM landscape offers several powerful families of models suitable for these tasks.

* **Llama 3 Family (Meta):** This series of models (8B, 70B, 405B parameters) represents the state-of-the-art in open-source LLMs. They demonstrate top-tier performance on a wide array of benchmarks, including reasoning,
  instruction following, and summarization.32 The models have a large vocabulary for efficient tokenization and have been trained on a massive, high-quality dataset, including a significant portion of non-English data.33
  Research indicates that fine-tuning can further enhance their summarization capabilities.35
* **Mixtral Family (Mistral AI):** These models employ a sparse Mixture-of-Experts (SMoE) architecture, which allows them to achieve the performance of much larger models while using only a fraction of their parameters
  during inference.37 This results in significantly faster inference speeds and lower computational costs.38 Mixtral models are known for their strong performance in multilingual contexts, mathematics, and code
  generation.32
* **Command R+ (Cohere):** This is a 104-billion parameter model specifically optimized for enterprise applications, with a focus on complex RAG and multi-step tool use (agentic workflows).41 It excels in multilingual
  settings and has built-in features to provide citations with its responses, which helps to mitigate hallucinations and ground its output in source data.43

#### **Hardware Considerations for Self-Hosting**

The primary constraint for deploying these models on private infrastructure is the significant hardware requirement, particularly GPU VRAM.

* **Entry-Level (e.g., Llama 3 8B, Mistral 7B):** Running smaller models with reasonable performance requires a modern consumer-grade or prosumer GPU. A minimum of 12GB of VRAM (e.g., NVIDIA RTX 3060\) is often cited,
  with 16-24GB (e.g., NVIDIA RTX 3090/4090) being strongly recommended for smoother operation and handling longer contexts.45 System RAM of 32-64GB is also advisable.46
* **High-End (e.g., Llama 3 70B, Command R+):** Larger models demand enterprise-grade hardware. A full-precision Llama 3 70B model requires over 140GB of VRAM, necessitating a multi-GPU setup with accelerators like the
  NVIDIA A100 (80GB).48 Similarly, Command R+ and Mixtral 8x22B are in a class that pushes beyond even a dual RTX 3090 setup.49
* **The Necessity of Quantization:** For most self-hosted deployments, running full-precision models is not feasible. Quantization is a technique that reduces the precision of the model's weights (e.g., from 16-bit to
  4-bit), drastically lowering VRAM and memory requirements at the cost of a minor reduction in accuracy.50 Using quantized formats like GGUF can make it possible to run a 70B parameter model on a system with 40-50GB of
  VRAM, bringing it within the realm of possibility for a high-end workstation or a single powerful server.48

The choice of LLM is therefore not simply about selecting the top-performing model on a benchmark leaderboard. It is a pragmatic exercise in balancing desired capability against a realistic hardware budget and the
acceptable trade-offs of quantization.

### **B. Swappable Vector Databases: The RAG Memory Core**

The vector database is the heart of the RAG system's retrieval capability. It stores vector embeddings—numerical representations of the knowledge base content—and enables fast and scalable semantic similarity searches.51

#### **Database Options and Analysis**

* **Qdrant:** An open-source vector database built in Rust, consistently praised for its performance, reliability, and efficiency.52 Multiple independent benchmarks show Qdrant achieving the highest requests per second (
  RPS) and lowest query latencies among its open-source peers.53 It offers advanced features like scalar quantization to reduce memory usage and powerful payload filtering, which allows for combining metadata filters
  with vector searches.52 It is often cited as the price-performance leader.54
* **Weaviate:** An AI-native, open-source vector database known for its rich, "batteries-included" feature set.56 It offers built-in modules for data vectorization, hybrid search (combining keyword and vector search),
  and has a wide range of integrations with the broader ML ecosystem.56 While feature-rich, some recent benchmarks suggest its raw performance has not kept pace with competitors like Qdrant.53
* **Milvus:** A highly scalable open-source vector database designed for massive-scale deployments, capable of handling tens of billions of vectors.57 It boasts the largest community and is often the fastest at indexing
  new data.53 Its architecture is more complex, offering multiple deployment modes (Lite, Standalone, Distributed) and various index types to suit different needs.55 In some query scenarios, its latency and throughput
  can be higher than Qdrant's.53

While raw query speed is a primary consideration, the optimal vector database must also support the specific query patterns of the RAG application. For a knowledge base with rich, versioned metadata (e.g., source URL,
creation date, document version), the ability to perform efficient, pre-filtered semantic searches is paramount. This allows the RAG system to first narrow the search space based on metadata (e.g., "find information only
in documents updated in the last month") before performing the vector search, improving both speed and relevance. Qdrant's well-regarded and performant filtering capabilities make it particularly well-suited for this
kind of sophisticated workflow.52

### **C. Recommendation for the RAG Core**

* **Language Model:** The recommended starting point is **Llama 3 8B Instruct**. This model provides an exceptional balance of performance and achievable hardware requirements for a self-hosted environment.58 It is more
  than capable of handling the summarization and structuring tasks required by the agents. The system's modular architecture should be designed to facilitate an upgrade path to a larger, quantized model such as  
  **Llama 3 70B** or **Mixtral 8x7B** as hardware resources permit.
* **Vector Database:** The recommended vector database is **Qdrant**. Its consistent top-tier performance in benchmarks, efficient resource management through quantization, and critically, its powerful and fast metadata
  filtering capabilities make it the ideal choice for this project.52 It provides the necessary functionality to build a sophisticated RAG system that can effectively query a versioned and richly annotated knowledge
  base.

The following tables provide a practical comparison of feasible LLMs for self-hosting and a feature comparison of the leading vector databases.

| Model            | Parameters       | Key Strengths (Summarization/Structuring)                                         | Estimated VRAM (Quantized) | Recommended Hardware Tier                                          |
|:-----------------|:-----------------|:----------------------------------------------------------------------------------|:---------------------------|:-------------------------------------------------------------------|
| **Llama 3 8B**   | 8B               | Excellent instruction following, strong reasoning for its size, efficient 33      | \~6-8 GB                   | Consumer (e.g., RTX 3060 12GB) 46                                  |
| **Mixtral 8x7B** | 47B (13B active) | High efficiency (SMoE), strong multilingual and code performance 37               | \~30-40 GB                 | Prosumer/Workstation (e.g., RTX 3090/4090 24GB) 60                 |
| **Llama 3 70B**  | 70B              | State-of-the-art performance, excels at complex reasoning and generation 58       | \~40-50 GB                 | High-End Workstation/Server (e.g., 2x RTX 3090 or 1x A100 80GB) 48 |
| **Command R+**   | 104B             | Optimized for RAG and tool use, provides citations, strong in enterprise tasks 42 | \~60-70 GB                 | High-End Server (e.g., 2x NVIDIA A6000) 49                         |

| Feature/Metric         | Qdrant                                                  | Weaviate                             | Milvus                                                      |
|:-----------------------|:--------------------------------------------------------|:-------------------------------------|:------------------------------------------------------------|
| **Core Technology**    | Rust 52                                                 | Go 56                                | C++ 57                                                      |
| **Latency (ms)**       | **Excellent:** Often the lowest in benchmarks 53        | Good                                 | Good, but can be higher in some scenarios 53                |
| **Throughput (RPS)**   | **Excellent:** Often the highest in benchmarks 53       | Good                                 | Good                                                        |
| **Indexing Speed**     | Good                                                    | Good                                 | **Excellent:** Often the fastest to index new data 53       |
| **Metadata Filtering** | **Excellent:** Powerful and performant pre-filtering 52 | Good: Supports advanced filtering 56 | Good: Supports metadata filtering 57                        |
| **Scalability**        | High; cloud-native design 52                            | High; supports horizontal scaling 56 | **Excellent:** Designed for massive scale (10B+ vectors) 57 |

## **V. Synthesizing the System: A Unified Architectural Blueprint**

This final section integrates the individual component recommendations into a single, cohesive system design. It outlines the complete technology stack and provides a narrative walkthrough of the system's end-to-end
workflow, illustrating how the autonomous agents continuously enrich the knowledge base.

### **A. Recommended Stack and Component Integration**

The proposed architecture is a tightly integrated system where each component plays a specialized role, orchestrated by a central state machine.

* **Orchestration Framework:** **LangGraph** will serve as the system's brain, managing the complex, cyclical workflow of research and knowledge curation as a stateful graph.
* **Research Toolkit:** A hybrid set of tools will be available to the agents: **Scrapy** for high-speed, bulk extraction of static web content, and **Playwright** for targeted interaction with dynamic, JavaScript-heavy
  websites.
* **Knowledge Base:** **BookStack** will act as the persistent source of truth, providing a structured, versioned repository for curated knowledge that is programmatically accessible via its REST API.
* **Language Model:** **Llama 3 8B Instruct** will be the initial model for summarization, structuring, and planning tasks, chosen for its optimal balance of performance and self-hosting feasibility.
* **Vector Database:** **Qdrant** will store the vector embeddings of the knowledge base content, enabling fast and accurate semantic retrieval for the RAG application, enhanced by its powerful metadata filtering.

The system operates as a continuous loop. The LangGraph orchestrator directs agents to use the research toolkit to gather new information. This information is then processed by the LLM and written into the BookStack
knowledge base via its API. A separate process monitors BookStack for changes and updates the Qdrant vector index, making the new knowledge immediately available for retrieval.

### **B. Workflow Example: From Research Trigger to Knowledge Base Update**

The following step-by-step process illustrates the system in action, demonstrating the flow of data and control through the integrated components.

1. **Trigger:** The workflow is initiated. This can be a scheduled trigger (e.g., a cron job that initiates a daily check on a set of key sources), an event-based trigger (e.g., a low-confidence answer from the RAG
   system flags a knowledge gap), or a manual trigger from a human administrator.
2. **Planning (LangGraph):** The LangGraph application is invoked and enters a "Planning" state. A "Planner" agent, powered by the Llama 3 model, receives the initial goal (e.g., "Research the latest developments in
   agentic AI frameworks"). It breaks this goal down into a concrete, multi-step plan, such as: \`\`. This plan is stored in the graph's state object.
3. **Research (LangGraph \+ Scrapy/Playwright):** The graph transitions to a "Research" state, iterating through the identified source URLs. For each URL, a "Research" agent first performs a lightweight check. If the
   content appears to be static HTML, it invokes the **Scrapy** tool for fast extraction. If the check indicates a dynamic, JavaScript-driven site, it escalates and invokes the **Playwright** tool to fully render the
   page and extract the content. The raw, unstructured text from each source is collected and added to the state object. If a tool fails, LangGraph's logic can handle retries or mark the source as inaccessible.
4. **Synthesis (LangGraph \+ LLM):** Once research is complete, the graph enters a "Synthesis" state. A "Synthesizer" agent takes the collected raw text from all sources. It uses a series of prompts with the **Llama 3**
   model to first summarize the key findings from each source and then synthesize them into a single, coherent document. A final prompt instructs the model to structure this synthesized knowledge into a predefined JSON
   object with fields like title, summary, key\_features, pros, cons, and source\_urls.
5. **Update Knowledge Base (LangGraph \+ BookStack API):** The graph transitions to an "Update" state. A "Writer" agent takes the structured JSON output. It uses the **BookStack REST API** to first search for an existing
   page with a similar title.
    * If a relevant page exists, the agent performs a PUT request to the /api/pages/{id} endpoint, providing the new content. BookStack automatically creates a new *page revision*, preserving the old version.
    * If no page exists, the agent performs a POST request to the /api/pages endpoint, creating a new page within the appropriate Book and Chapter.
6. **Indexing (BookStack → Qdrant):** This process runs asynchronously to the main agent workflow. A separate service (e.g., a webhook receiver or a polling mechanism) detects the creation or update of a page in
   BookStack. This service retrieves the new content, splits it into meaningful chunks, generates vector embeddings for each chunk using an open-source sentence-transformer model, and upserts these vectors into **Qdrant
   **. Each vector is stored with associated metadata, including the BookStack page\_id, book\_id, and revision\_id.
7. **Completion:** The LangGraph workflow concludes, logging its success and the URL of the newly updated or created BookStack page. The new, structured knowledge is now fully indexed in Qdrant and immediately available
   to the RAG system for querying.

### **C. Concluding Remarks on Future-Proofing the System**

This proposed architecture is designed not only to meet the immediate requirements but also to be adaptable and scalable for the future.

* **Modularity:** The clear separation of concerns ensures that individual components can be upgraded without requiring a full system redesign. As more powerful and efficient open-source LLMs become available, the Llama
  3 8B model can be swapped out by simply updating the API endpoint used by the agents. Similarly, the vector database can be replaced by modifying only the final indexing service, leaving the core agentic workflow
  untouched.
* **Human-in-the-Loop:** The stateful nature of the LangGraph orchestrator makes it straightforward to introduce human oversight. An additional "Verification" state can be added to the workflow. In this state, the agent
  would post a draft to BookStack with a "pending review" tag and pause the workflow. The system would only proceed to the final indexing step after receiving an approval signal from a human reviewer, either through the
  BookStack UI or a dedicated API call.
* **Scalability:** The most computationally intensive parts of the system are the browser automation (Playwright) and LLM inference. The architecture allows these components to be scaled independently. They can be
  deployed as distinct microservices on dedicated hardware (e.g., a GPU server for the LLM, a CPU-heavy cluster for Playwright instances). The LangGraph agents would then interact with these services via internal API
  calls, allowing the core orchestration logic to remain lightweight while the heavy computational tasks are handled by scalable, specialized workers. This distributed model ensures the system can grow to handle
  increasing research loads and more complex processing tasks over time.

#### **Works cited**

1. Best AI Agent Frameworks by Category in 2025 (Open-Source & Proprietary) \- Bitcot, accessed on September 19,
   2025, [https://www.bitcot.com/best-ai-agent-frameworks-by-category/](https://www.bitcot.com/best-ai-agent-frameworks-by-category/)
2. Framework for orchestrating role-playing, autonomous AI agents. By fostering collaborative intelligence, CrewAI empowers agents to work together seamlessly, tackling complex tasks. \- GitHub, accessed on September 19,
   2025, [https://github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
3. Autogen vs LangChain vs CrewAI: Our AI Engineers' Ultimate Comparison Guide, accessed on September 19,
   2025, [https://www.instinctools.com/blog/autogen-vs-langchain-vs-crewai/](https://www.instinctools.com/blog/autogen-vs-langchain-vs-crewai/)
4. OpenAI Agents SDK vs LangGraph vs Autogen vs CrewAI \- Composio, accessed on September 19,
   2025, [https://composio.dev/blog/openai-agents-sdk-vs-langgraph-vs-autogen-vs-crewai](https://composio.dev/blog/openai-agents-sdk-vs-langgraph-vs-autogen-vs-crewai)
5. My thoughts on the most popular frameworks today: crewAI, AutoGen, LangGraph, and OpenAI Swarm : r/LangChain \- Reddit, accessed on September 19,
   2025, [https://www.reddit.com/r/LangChain/comments/1g6i7cj/my\_thoughts\_on\_the\_most\_popular\_frameworks\_today/](https://www.reddit.com/r/LangChain/comments/1g6i7cj/my_thoughts_on_the_most_popular_frameworks_today/)
6. AutoGen \- AWS Prescriptive Guidance, accessed on September 19,
   2025, [https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/autogen.html](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/autogen.html)
7. LangChain, AutoGen, and CrewAI. Which AI Framework is Right for You in… | by Yashwant Deshmukh | Medium, accessed on September 19,
   2025, [https://medium.com/@yashwant.deshmukh23/langchain-autogen-and-crewai-2593e7645de7](https://medium.com/@yashwant.deshmukh23/langchain-autogen-and-crewai-2593e7645de7)
8. Microsoft AutoGen: Orchestrating Multi-Agent LLM Systems | Tribe AI, accessed on September 19,
   2025, [https://www.tribe.ai/applied-ai/microsoft-autogen-orchestrating-multi-agent-llm-systems](https://www.tribe.ai/applied-ai/microsoft-autogen-orchestrating-multi-agent-llm-systems)
9. microsoft/autogen: A programming framework for agentic AI \- GitHub, accessed on September 19, 2025, [https://github.com/microsoft/autogen](https://github.com/microsoft/autogen)
10. AutoGen \- Microsoft, accessed on September 19,
    2025, [https://www.microsoft.com/en-us/research/wp-content/uploads/2025/01/WEF-2025\_Leave-Behind\_AutoGen.pdf](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/01/WEF-2025_Leave-Behind_AutoGen.pdf)
11. AutoGen \- Microsoft Research, accessed on September 19, 2025, [https://www.microsoft.com/en-us/research/project/autogen/](https://www.microsoft.com/en-us/research/project/autogen/)
12. LangChain, accessed on September 19, 2025, [https://www.langchain.com/](https://www.langchain.com/)
13. Best 30+ Open Source Web Agents \- Research AIMultiple, accessed on September 19, 2025, [https://research.aimultiple.com/open-source-web-agents/](https://research.aimultiple.com/open-source-web-agents/)
14. Scrapy vs Playwright: Web Scraping Comparison Guide \- Bright Data, accessed on September 19,
    2025, [https://brightdata.com/blog/web-data/scrapy-vs-playwright](https://brightdata.com/blog/web-data/scrapy-vs-playwright)
15. Scrapy vs. Playwright: A Comparison for Web Scraping \- Medium, accessed on September 19,
    2025, [https://medium.com/@datajournal/scrapy-vs-playwright-4db74c4ebd95](https://medium.com/@datajournal/scrapy-vs-playwright-4db74c4ebd95)
16. Scrapy vs Playwright \- Medium, accessed on September 19, 2025, [https://medium.com/@amit25173/scrapy-vs-playwright-112e896f7679](https://medium.com/@amit25173/scrapy-vs-playwright-112e896f7679)
17. Scrapy vs. Selenium for Web Scraping \- Bright Data, accessed on September 19, 2025, [https://brightdata.com/blog/web-data/scrapy-vs-selenium](https://brightdata.com/blog/web-data/scrapy-vs-selenium)
18. Read the Docs: Full featured documentation deployment platform, accessed on September 19, 2025, [https://about.readthedocs.com/](https://about.readthedocs.com/)
19. BookStack, accessed on September 19, 2025, [https://www.bookstackapp.com/](https://www.bookstackapp.com/)
20. Hacking BookStack, accessed on September 19, 2025, [https://www.bookstackapp.com/docs/admin/hacking-bookstack/](https://www.bookstackapp.com/docs/admin/hacking-bookstack/)
21. Docusaurus: Build optimized websites quickly, focus on your content, accessed on September 19, 2025, [https://docusaurus.io/](https://docusaurus.io/)
22. Introduction | Docusaurus, accessed on September 19, 2025, [https://docusaurus.io/docs](https://docusaurus.io/docs)
23. Versioning \- Docusaurus, accessed on September 19, 2025, [https://docusaurus.io/docs/versioning](https://docusaurus.io/docs/versioning)
24. Wiki.js, accessed on September 19, 2025, [https://js.wiki/](https://js.wiki/)
25. Requirements \- Wiki.js \- requarks.io, accessed on September 19, 2025, [https://docs.requarks.io/install/requirements](https://docs.requarks.io/install/requirements)
26. Git \- Wiki.js \- requarks.io, accessed on September 19, 2025, [https://docs.requarks.io/storage/git](https://docs.requarks.io/storage/git)
27. Storage \- Wiki.js \- requarks.io, accessed on September 19, 2025, [https://docs.requarks.io/storage](https://docs.requarks.io/storage)
28. Wiki.js, accessed on September 19, 2025, [https://beta.js.wiki/](https://beta.js.wiki/)
29. API Documentation \- BookStack, accessed on September 19, 2025, [https://bookstack.bassopaolo.com/api/docs](https://bookstack.bassopaolo.com/api/docs)
30. Evaluating Large Language Models for Structured Science Summarization in the Open Research Knowledge Graph \- MDPI, accessed on September 19,
    2025, [https://www.mdpi.com/2078-2489/15/6/328](https://www.mdpi.com/2078-2489/15/6/328)
31. LLM Summarization: Techniques, Metrics, and Top Models \- ProjectPro, accessed on September 19,
    2025, [https://www.projectpro.io/article/llm-summarization/1082](https://www.projectpro.io/article/llm-summarization/1082)
32. The 11 best open-source LLMs for 2025 \- n8n Blog, accessed on September 19, 2025, [https://blog.n8n.io/open-source-llm/](https://blog.n8n.io/open-source-llm/)
33. Introducing Meta Llama 3: The most capable openly available LLM to date, accessed on September 19, 2025, [https://ai.meta.com/blog/meta-llama-3/](https://ai.meta.com/blog/meta-llama-3/)
34. Unlocking Llama 3.1: Comprehensive Insights & Benchmarks \- MyScale, accessed on September 19,
    2025, [https://myscale.com/blog/top-5-insights-llama-3-1-performance-benchmarks/](https://myscale.com/blog/top-5-insights-llama-3-1-performance-benchmarks/)
35. Benchmarking Llama 3 for Chinese News Summation: Accuracy, Cultural Nuance, and Societal Value Alignment \- ResearchGate, accessed on September 19,
    2025, [https://www.researchgate.net/publication/381145759\_Benchmarking\_Llama\_3\_for\_Chinese\_News\_Summation\_Accuracy\_Cultural\_Nuance\_and\_Societal\_Value\_Alignment](https://www.researchgate.net/publication/381145759_Benchmarking_Llama_3_for_Chinese_News_Summation_Accuracy_Cultural_Nuance_and_Societal_Value_Alignment)
36. Evaluating LLMs and Pre-trained Models for Text Summarization Across Diverse Datasets, accessed on September 19, 2025, [https://arxiv.org/html/2502.19339v2](https://arxiv.org/html/2502.19339v2)
37. Mixtral of experts \- Mistral AI, accessed on September 19, 2025, [https://mistral.ai/news/mixtral-of-experts](https://mistral.ai/news/mixtral-of-experts)
38. Mixtral | Prompt Engineering Guide, accessed on September 19, 2025, [https://www.promptingguide.ai/models/mixtral](https://www.promptingguide.ai/models/mixtral)
39. Models Benchmarks \- Mistral AI Documentation, accessed on September 19, 2025, [https://docs.mistral.ai/getting-started/models/benchmark/](https://docs.mistral.ai/getting-started/models/benchmark/)
40. Mixtral 8x22B by Mistral AI Crushes Benchmarks in 4+ Languages \- Analytics Vidhya, accessed on September 19,
    2025, [https://www.analyticsvidhya.com/blog/2024/04/mixtral-8x22b-by-mistral-ai/](https://www.analyticsvidhya.com/blog/2024/04/mixtral-8x22b-by-mistral-ai/)
41. Command R+ vs. Llama 3 vs. Mixtral 8x22B Comparison \- SourceForge, accessed on September 19,
    2025, [https://sourceforge.net/software/compare/Command-R-Plus-vs-Llama-3-vs-Mixtral-8x22B/](https://sourceforge.net/software/compare/Command-R-Plus-vs-Llama-3-vs-Mixtral-8x22B/)
42. Cohere's Command R+ Model, accessed on September 19, 2025, [https://docs.cohere.com/docs/command-r-plus](https://docs.cohere.com/docs/command-r-plus)
43. CohereLabs/c4ai-command-r-plus \- Hugging Face, accessed on September 19, 2025, [https://huggingface.co/CohereLabs/c4ai-command-r-plus](https://huggingface.co/CohereLabs/c4ai-command-r-plus)
44. Papers Explained 166: Command Models | by Ritvik Rastogi \- Medium, accessed on September 19,
    2025, [https://ritvik19.medium.com/papers-explained-166-command-r-models-94ba068ebd2b](https://ritvik19.medium.com/papers-explained-166-command-r-models-94ba068ebd2b)
45. 6 Self-Hosted & Local LLMs \- Budibase, accessed on September 19, 2025, [https://budibase.com/blog/ai-agents/local-llms/](https://budibase.com/blog/ai-agents/local-llms/)
46. LLaMA 3.3 System Requirements: What You Need to Run It Locally, accessed on September 19,
    2025, [https://www.oneclickitsolution.com/centerofexcellence/aiml/llama-3-3-system-requirements-run-locally](https://www.oneclickitsolution.com/centerofexcellence/aiml/llama-3-3-system-requirements-run-locally)
47. Mistral 7B System Requirements: What You Need to Run It Locally, accessed on September 19,
    2025, [https://www.oneclickitsolution.com/centerofexcellence/aiml/run-mistral-7b-locally-hardware-software-specs](https://www.oneclickitsolution.com/centerofexcellence/aiml/run-mistral-7b-locally-hardware-software-specs)
48. GPU Requirement Guide for Llama 3 (All Variants) \- ApX Machine Learning, accessed on September 19,
    2025, [https://apxml.com/posts/ultimate-system-requirements-llama-3-models](https://apxml.com/posts/ultimate-system-requirements-llama-3-models)
49. Is it possible to run Command R+ with 64GB RAM \+ 12GB VRAM? : r/LocalLLaMA \- Reddit, accessed on September 19,
    2025, [https://www.reddit.com/r/LocalLLaMA/comments/1c1zdnr/is\_it\_possible\_to\_run\_command\_r\_with\_64gb\_ram/](https://www.reddit.com/r/LocalLLaMA/comments/1c1zdnr/is_it_possible_to_run_command_r_with_64gb_ram/)
50. Self-Hosting LLMs in 2025: Complete Guide for Privacy & Cost Savings \- Kextcache, accessed on September 19,
    2025, [https://kextcache.com/self-hosting-llms-privacy-cost-efficiency-guide/](https://kextcache.com/self-hosting-llms-privacy-cost-efficiency-guide/)
51. Self-Hosted LLM: A 5-Step Deployment Guide, accessed on September 19, 2025, [https://www.plural.sh/blog/self-hosting-large-language-models/](https://www.plural.sh/blog/self-hosting-large-language-models/)
52. Qdrant \- Vector Database \- Qdrant, accessed on September 19, 2025, [https://qdrant.tech/](https://qdrant.tech/)
53. Vector Database Benchmarks \- Qdrant, accessed on September 19, 2025, [https://qdrant.tech/benchmarks/](https://qdrant.tech/benchmarks/)
54. Picking a vector database: a comparison and guide for 2023, accessed on September 19, 2025, [https://benchmark.vectorview.ai/vectordbs.html](https://benchmark.vectorview.ai/vectordbs.html)
55. Top Vector Databases for Enterprise AI in 2025: Complete Selection Guide | by Balaram Panda \- Medium, accessed on September 19,
    2025, [https://medium.com/@balarampanda.ai/top-vector-databases-for-enterprise-ai-in-2025-complete-selection-guide-39c58cc74c3f](https://medium.com/@balarampanda.ai/top-vector-databases-for-enterprise-ai-in-2025-complete-selection-guide-39c58cc74c3f)
56. Open Source Vector Database | Weaviate, accessed on September 19, 2025, [https://weaviate.io/platform](https://weaviate.io/platform)
57. Milvus | High-Performance Vector Database Built for Scale, accessed on September 19, 2025, [https://milvus.io/](https://milvus.io/)
58. What is Llama 3? The Experts' View on The Next Generation of Open Source LLMs, accessed on September 19,
    2025, [https://www.datacamp.com/blog/meta-announces-llama-3-the-next-generation-of-open-source-llms](https://www.datacamp.com/blog/meta-announces-llama-3-the-next-generation-of-open-source-llms)
59. Llama 3's Performance Benchmark Values Explained | by Ingrid Stevens \- Medium, accessed on September 19,
    2025, [https://medium.com/@ingridwickstevens/more-llm-acronyms-an-explainer-on-llama-3s-performance-benchmark-values-36722c6dcabb](https://medium.com/@ingridwickstevens/more-llm-acronyms-an-explainer-on-llama-3s-performance-benchmark-values-36722c6dcabb)
60. How to Run a Self-Hosted LLM Without Going Overboard, accessed on September 19, 2025, [https://blog.ishosting.com/en/self-hosted-llm](https://blog.ishosting.com/en/self-hosted-llm)
