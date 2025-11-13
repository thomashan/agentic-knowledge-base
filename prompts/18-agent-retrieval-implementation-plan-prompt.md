**Title:** Implementation Plan for `agents-retrieval`

**Persona:** You are Gemini, an expert TDD Software Engineer.

**Context:** The `agents-knowledge` package is complete, which means the system can now persist information into a vector database (`Qdrant`). The next logical step is to create an agent that can retrieve this
information.

**Goal:** Create a comprehensive, test-driven implementation plan for the `agents-retrieval` package.

**Deliverable:**
A single markdown file containing the complete implementation plan.

**Acceptance Criteria for the Plan:**

1. **Goal and Vision:** The plan must define the `RetrievalAgent`'s primary role: to query the vector database for information relevant to a given query or topic. This agent will be a crucial component of the RAG loop,
   providing context to other agents.

2. **Core Components and Data Models:**
    * The plan must specify the agent's input, which will be a simple query string.
    * It must define the output data model, `RetrievalResult`, which should contain a list of retrieved document chunks with their content, metadata, and similarity scores.

3. **High-Level Workflow:** The plan must detail the agent's end-to-end workflow:
    * Receiving a query string.
    * Using an embedding model to generate a vector embedding for the query.
    * Using the `QdrantTool` (from the `integration-vectordb` package) to perform a similarity search in the vector database.
    * Formatting the results from the `QdrantTool` into a `RetrievalResult` object.

4. **TDD Implementation Cycle:** The plan must detail a RED-GREEN-REFACTOR cycle for the `agents-retrieval` package.
    * Specify the test files to be created (`test_retrieval_models.py`, `test_retrieval_agent_unit.py`, `test_retrieval_agent_integration.py`).
    * Describe unit tests using a **mock `QdrantTool`** and a **mock embedding model** to test the agent's logic in isolation.
    * Describe an **integration test** that uses a **real embedding model** and a concrete `QdrantTool` instance to verify the full data flow. The Qdrant client itself will be mocked to avoid network calls.

5. **Project Conventions:** The plan must adhere to all existing project conventions (e.g., use of `AbstractAgent`, dependency injection for tools/LLMs).

6. **Output File:** The final plan must be written to the file: `prompts/gemini-cli/18-agent-retrieval-implementation-plan.md`.
