### **Implementation Plan: `agents-retrieval`**

#### **1. Project Goal & Vision**

The `agents-retrieval` project will introduce the `RetrievalAgent`, a specialized agent that forms the core of the "Retrieval" in our RAG system. Its sole purpose is to retrieve relevant information from the `Qdrant`
vector database based on a natural language query. This agent will provide the foundational context that other agents, like the `IntelligenceAgent`, will use to generate insights and reports.

#### **2. Core Components & Data Models**

**File: `app/agents-retrieval/src/agents_retrieval/models.py`**

```python
from typing import List, Dict, Any

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """Represents a single chunk of retrieved information."""
    document_url: str = Field(description="The source URL of the document the chunk belongs to.")
    text: str = Field(description="The text content of the chunk.")
    score: float = Field(description="The similarity score of the chunk to the query.")
    metadata: Dict[str, Any] = Field(description="Other metadata associated with the chunk.")


class RetrievalResult(BaseModel):
    """The output of a retrieval operation, containing relevant chunks."""
    query: str = Field(description="The original query string.")
    retrieved_chunks: List[RetrievedChunk] = Field(description="A list of the most relevant chunks found.")
```

#### **3. High-Level Workflow of the `RetrievalAgent`**

1. The `RetrievalAgent` receives a natural language query string as input.
2. It uses an embedding model (e.g., from `sentence-transformers`) to generate a vector embedding for the query.
3. It calls the `QdrantTool`'s `search` command (which will need to be added to the tool), passing the query vector and the target collection name (`knowledge_base`).
4. The `QdrantTool` performs a similarity search in the Qdrant database and returns a list of `ScoredPoint` objects.
5. The `RetrievalAgent` processes the list of `ScoredPoint` objects, transforming them into a list of `RetrievedChunk` models.
6. Finally, it returns a `RetrievalResult` object containing the original query and the list of retrieved chunks.

#### **4. TDD Implementation Cycle**

The implementation will require adding a new `search` command to the existing `integration-vectordb` package, and then building the new `agents-retrieval` package.

**Part 1: Enhance `integration-vectordb` Package**

1. **RED (Test):** Open `app/integration-vectordb/tests/test_qdrant_tool.py`. Add a new test, `test_search_vectors`, that mocks the `qdrant_client` and asserts that its `search` method is called with the correct vector
   and parameters. This test will fail.
2. **GREEN (Code):** Open `app/integration-vectordb/src/integration_vectordb/qdrant_tool.py`. Implement the `search_vectors` method.
3. **REFACTOR:** Update the `execute` method in `QdrantTool` to dispatch a `search` command to the new `search_vectors` method. Add a test for this dispatch logic.

**Part 2: `agents-retrieval` Package**

1. **RED (Models):** Create `app/agents-retrieval/tests/test_retrieval_models.py`. Write tests to validate the `RetrievedChunk` and `RetrievalResult` Pydantic models. The tests will fail.
2. **GREEN (Models):** Create `app/agents-retrieval/src/agents_retrieval/models.py` and implement the models to make the tests pass.

3. **RED (Unit Test):** Create `app/agents-retrieval/tests/test_retrieval_agent_unit.py`. Write a test for the `RetrievalAgent`.
    * Instantiate the agent with a **mock `QdrantTool`** and a **mock embedding model**.
    * Mock the return value of the `qdrant_tool.execute` to be a list of sample `ScoredPoint` objects.
    * Call the agent's primary method (e.g., `.retrieve()`) with a sample query.
    * Assert that the embedding model's `encode` method was called.
    * Assert that the `qdrant_tool.execute` method was called with the `search` command.
    * Assert that the agent correctly processes the mock `ScoredPoint` objects and returns a valid `RetrievalResult`.
    * This test will fail as the agent does not exist.
4. **GREEN (Unit Test):** Create `app/agents-retrieval/src/agents_retrieval/retrieval.py`. Implement the `RetrievalAgent` class and its `retrieve` method to make the unit test pass.

5. **RED (Integration Test):** Create `app/agents-retrieval/tests/test_retrieval_agent_integration.py`. Write an integration test.
    * Instantiate the `RetrievalAgent` with a **real `QdrantTool`** and a **real embedding model** (e.g., `all-MiniLM-L6-v2`).
    * Mock the `qdrant_client` at the class level to control the `search` method's return value, simulating a real Qdrant response.
    * Call the agent's `.retrieve()` method.
    * Assert that the agent correctly processes the realistic Qdrant response and returns a `RetrievalResult` with the expected structure and data.
    * This test will likely fail initially due to integration complexities.
6. **GREEN (Integration Test):** Debug and refine the agent and tool implementations until the integration test passes.

7. **REFACTOR:** Review all new code for quality, clarity, and documentation, ensuring all tests continue to pass.
