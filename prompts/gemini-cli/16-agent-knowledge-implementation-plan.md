### **Implementation Plan: `agents-knowledge`**

#### **1. Project Goal & Vision**

The `agents-knowledge` project will create a specialist agent responsible for the critical task of knowledge persistence. This `KnowledgeAgent` will act as the bridge between the `IntelligenceAgent`'s synthesized insights and the system's long-term memory. Its primary function is to take a structured `IntelligenceReport` and write it to two destinations: the `Outline` documentation platform for human consumption and the `Qdrant` vector database for machine retrieval, thus completing the core data ingestion loop of the RAG system.

#### **2. Core Components & Data Models**

This implementation will introduce three new packages: two tool packages (`integration-documentation`, `integration-vectordb`) and the agent package itself (`agents-knowledge`).

**File: `app/agents-knowledge/src/agents_knowledge/models.py`**

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any
# The agent's primary input is the report from the intelligence agent.
from agents_intelligence.models import IntelligenceReport


class DocumentChunk(BaseModel):
    """Represents a single chunk of text to be vectorized."""
    chunk_id: str = Field(description="A unique identifier for the chunk (e.g., 'doc-123-chunk-0').")
    text: str = Field(description="The text content of the chunk.")
    metadata: Dict[str, Any] = Field(description="Metadata associated with the chunk, like source URL.")


class KnowledgePersistenceResult(BaseModel):
    """The output confirming the successful persistence of knowledge."""
    document_url: str = Field(description="The URL of the created or updated document in Outline.")
    vector_ids: List[str] = Field(description="A list of the unique IDs for the vectors upserted into Qdrant.")
```

#### **3. New Integration Packages & Tools**

Two new tool packages will be created, each providing a concrete implementation of the `AbstractTool` interface.

1.  **Package: `app/integration-documentation`**
    *   **Tool:** `OutlineTool`
    *   **Purpose:** To wrap the `Outline` REST API for creating and updating documents.
    *   **Methods:** A key method will be `create_or_update_document(title: str, content: str) -> str`, which returns the URL of the document.

2.  **Package: `app/integration-vectordb`**
    *   **Tool:** `QdrantTool`
    *   **Purpose:** To wrap the `qdrant-client` for interacting with the Qdrant database.
    *   **Methods:** A key method will be `upsert_vectors(collection_name: str, vectors: List[List[float]], payloads: List[Dict]) -> List[str]`, which returns the IDs of the upserted vectors.

#### **4. High-Level Workflow of the `KnowledgeAgent`**

1.  The `KnowledgeAgent` receives an `IntelligenceReport` object.
2.  It formats the report into a clean Markdown string suitable for documentation.
3.  It calls the `OutlineTool` to create or update a document with the formatted Markdown.
4.  It then takes the content, chunks it into smaller, semantically meaningful pieces using a text splitter (e.g., from `langchain_text_splitters`).
5.  For each chunk, it uses an embedding model (e.g., from `sentence-transformers`) to generate a vector embedding.
6.  It calls the `QdrantTool` to upsert the generated vectors and their associated metadata (like the Outline document URL) into the Qdrant database.
7.  Finally, it returns a `KnowledgePersistenceResult` object confirming the operation.

#### **5. TDD Implementation Cycle**

The implementation will proceed package by package, following a strict RED-GREEN-REFACTOR cycle for each.

**Part 1: `integration-documentation` Package**

1.  **RED:** Create `app/integration-documentation/tests/test_outline_tool.py`. Write a test that attempts to instantiate `OutlineTool` and call a `.create_or_update_document()` method. The test will use `pytest-mock` to mock the `requests` library to avoid making real API calls. It will assert that the `requests.post` or `requests.put` method is called with the correct URL and payload. This test will fail.
2.  **GREEN:** Create `app/integration-documentation/src/documentation/outline_tool.py`. Implement the `OutlineTool` class, inheriting from `AbstractTool`. Implement the `create_or_update_document` method with the minimal logic required to make the test pass.
3.  **REFACTOR:** Refine the tool's implementation, add error handling, and improve documentation.

**Part 2: `integration-vectordb` Package**

1.  **RED:** Create `app/integration-vectordb/tests/test_qdrant_tool.py`. Write a test that instantiates `QdrantTool` and calls `.upsert_vectors()`. Use `pytest-mock` to mock the `qdrant_client.QdrantClient` and assert that its `.upsert()` method is called with the expected arguments. This test will fail.
2.  **GREEN:** Create `app/integration-vectordb/src/integration_vectordb/qdrant_tool.py`. Implement the `QdrantTool` class and its `upsert_vectors` method to make the test pass.
3.  **REFACTOR:** Clean up the implementation.

**Part 3: `agents-knowledge` Package**

1.  **RED (Models):** Create `app/agents-knowledge/tests/test_models.py`. Write tests to validate the `DocumentChunk` and `KnowledgePersistenceResult` Pydantic models. The tests will fail.
2.  **GREEN (Models):** Implement the models in `app/agents-knowledge/src/agents_knowledge/models.py` to make the tests pass.

3.  **RED (Unit Test):** Create `app/agents-knowledge/tests/test_knowledge_agent_unit.py`. Write a test for the `KnowledgeAgent`.
    *   Instantiate the `KnowledgeAgent` with **mock** `OutlineTool` and **mock** `QdrantTool` objects.
    *   Call the agent's primary method (e.g., `.persist_report()`) with a sample `IntelligenceReport`.
    *   Assert that the `create_or_update_document` method on the mock `OutlineTool` was called once.
    *   Assert that the `upsert_vectors` method on the mock `QdrantTool` was called once.
    *   This test will fail as the agent does not exist.
4.  **GREEN (Unit Test):** Create `app/agents-knowledge/src/agents_knowledge/knowledge.py`. Implement the `KnowledgeAgent` class. Implement its `persist_report` method with the logic to call the tools as described in the workflow. Make the unit test pass.

5.  **RED (Integration Test):** Create `app/agents-knowledge/tests/test_knowledge_agent_integration.py`. Write an integration test.
    *   This test will instantiate the `KnowledgeAgent` with **real** (but locally configured) `OutlineTool` and `QdrantTool` instances.
    *   It will use a **real embedding model** to generate vectors.
    *   The external services (Outline API, Qdrant DB) will be mocked at the network level (`requests` and `qdrant_client`) to ensure the test remains isolated and fast.
    *   Call `.persist_report()` with a sample `IntelligenceReport`.
    *   Assert that the data passed to the mocked `requests.post` and mocked `qdrant_client.upsert` calls is correctly formatted (e.g., assert that the vectors are of the correct dimension).
    *   This test will likely fail initially due to integration complexities.
6.  **GREEN (Integration Test):** Debug and refine the agent and tool implementations until the integration test passes.

7.  **REFACTOR:** Review all three new packages for code quality, clarity, and documentation, ensuring all tests continue to pass.
