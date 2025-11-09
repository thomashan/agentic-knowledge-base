**Title:** Implementation Plan for `agents-knowledge`

**Persona:** You are Gemini, an expert TDD Software Engineer.

**Context:** The `integration-llm`, `agents-orchestrator-crewai`, `agents-planner`, `agents-research`, and `agents-intelligence` components are complete and tested. The next component to be built is `agents-knowledge`,
which is responsible for persisting the synthesized insights into the system's long-term memory.

**Goal:** Create a comprehensive, test-driven implementation plan for the `agents-knowledge` package and its required integration dependencies.

**Input Documents:**
Analyze and synthesize the common patterns and approaches for a "Knowledge Agent" from the following documents:

* `prompts/chatgpt/02-initial-implementation-deep-research.md`
* `prompts/claude/02-initial-implementation-opus-4.1.md`
* `prompts/copilot/02-initial-implementation-smart.md`
* `prompts/deepseek/02-initial-implementation-deepthink.md`
* `prompts/gemini/02-initial-implementation-gemini-2.5-pro-deep-research.md`
* `prompts/grok/02-initial-implementation-expert.md`
* `prompts/qwen/02-initial-implementation-qwen3-235b-a22b-2507.md`

**Deliverable:**
A single markdown file containing the complete implementation plan.

**Acceptance Criteria for the Plan:**

1. **Goal and Vision:** The plan must define the `KnowledgeAgent`'s primary role: to act as the bridge between synthesized insights and the system's long-term memory. It must persist knowledge into both a human-readable
   documentation platform (`Outline`) and a machine-readable vector database (`Qdrant`).

2. **Core Components and Data Models:**
    * The plan must specify the agent's input, which is the `IntelligenceReport` model from the `agents-intelligence` package.
    * It must define any new data models required for the persistence process (e.g., a model for a document chunk with its vector embedding).
    * Crucially, the plan must outline the creation of two new tool packages: `integration-documentation` to wrap the Outline API, and `integration-vectordb` to wrap the Qdrant client API.

3. **High-Level Workflow:** The plan must detail the agent's end-to-end workflow:
    * Receiving an `IntelligenceReport`.
    * Formatting the report content into a human-readable format (e.g., Markdown).
    * Using the `documentation_tool` to create or update a page in Outline.
    * Chunking the content for vectorization.
    * Using an embedding model to generate vectors for each chunk.
    * Using the `vectordb_tool` to upsert the vectors and their associated metadata into Qdrant.

4. **TDD Implementation Cycle:** The plan must detail a RED-GREEN-REFACTOR cycle for all three new packages (`integration-documentation`, `integration-vectordb`, and `agents-knowledge`).
    * For the two integration packages, the plan must describe creating `AbstractTool` implementations and the tests to validate their functionality (e.g., test creating a document in Outline, test upserting a vector to
      Qdrant).
    * For the `agents-knowledge` package, the plan must specify the test files (`test_models.py`, `test_knowledge_agent_unit.py`, `test_knowledge_agent_integration.py`).
    * It must describe unit tests using **mock tools** to test the agent's logic in isolation.
    * It must describe an **integration test** that uses a **real embedding model** and the concrete tool implementations to verify the full data flow from `IntelligenceReport` to the (mocked or local) external services.

5. **Project Conventions:** The plan must adhere to all existing project conventions (e.g., use of `AbstractAgent`, `AbstractTool`, dependency injection for tools/LLMs).

6. **Output File:** The final plan must be written to the file: `prompts/gemini-cli/16-agent-knowledge-implementation-plan.md`.
