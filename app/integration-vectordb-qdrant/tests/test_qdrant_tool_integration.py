import uuid
from typing import Any

import pytest
from agents_core.core import AbstractAgent, AbstractLLM, AbstractTask, AbstractTool
from crewai_adapter.adapter import CrewAIOrchestrator, CrewAILLM
from qdrant_client.http import models


@pytest.mark.integration
def test_upsert_and_retrieve_integration(qdrant_tool):
    """
    Tests upserting vectors to a Qdrant instance and then retrieving them
    to verify the operation was successful.
    """
    # Arrange
    collection_name = f"test_collection_{uuid.uuid4()}"
    vectors = [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]
    payloads = [{"meta": "first"}, {"meta": "second"}]
    ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    vector_size = len(vectors[0])

    # Ensure the collection exists or create it
    if not qdrant_tool._client.collection_exists(collection_name=collection_name):
        qdrant_tool._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )

    # Act: Upsert the vectors
    upserted_ids = qdrant_tool.upsert_vectors(collection_name=collection_name, vectors=vectors, payloads=payloads, ids=ids)

    # Assert: Verify the upsert operation
    assert upserted_ids == ids

    # Act: Retrieve the points to verify they were stored correctly
    retrieved_points = qdrant_tool._client.retrieve(
        collection_name=collection_name,
        ids=[ids[0]],
        with_payload=True,
    )

    # Assert: Verify the retrieved data
    assert len(retrieved_points) == 1
    assert retrieved_points[0].id == ids[0]
    assert retrieved_points[0].payload == payloads[0]

    # Clean up the collection
    qdrant_tool._client.delete_collection(collection_name=collection_name)


@pytest.mark.integration
def test_delete_vectors_integration(qdrant_tool):
    """
    Tests deleting vectors from a Qdrant instance and verifies they are no longer retrievable.
    """
    # Arrange
    collection_name = f"test_collection_delete_{uuid.uuid4()}"
    vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    payloads = [{"idx": 1}, {"idx": 2}, {"idx": 3}]
    ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    vector_size = len(vectors[0])

    if not qdrant_tool._client.collection_exists(collection_name=collection_name):
        qdrant_tool._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
        )
    qdrant_tool.upsert_vectors(collection_name=collection_name, vectors=vectors, payloads=payloads, ids=ids)

    # Act: Delete one vector
    qdrant_tool.delete_vectors(collection_name=collection_name, ids=[ids[1]])

    # Assert: Verify the deleted vector is not found, others are
    retrieved_points_all = qdrant_tool._client.retrieve(
        collection_name=collection_name,
        ids=ids,
        with_payload=True,
    )
    # The deleted ID should not be in the retrieved points
    retrieved_ids = [point.id for point in retrieved_points_all]
    assert ids[1] not in retrieved_ids
    assert ids[0] in retrieved_ids
    assert ids[2] in retrieved_ids
    assert len(retrieved_points_all) == 2  # Expecting 2 points after deleting one

    # Clean up
    qdrant_tool._client.delete_collection(collection_name=collection_name)


@pytest.mark.integration
def test_search_vectors_integration(qdrant_tool):
    """
    Tests searching for vectors in a Qdrant instance and verifies the results.
    """
    # Arrange
    collection_name = f"test_collection_search_{uuid.uuid4()}"
    vectors = [[0.1, 0.2, 0.9, 0.1], [0.9, 0.1, 0.1, 0.2], [0.4, 0.5, 0.8, 0.3]]
    payloads = [{"meta": "A"}, {"meta": "B"}, {"meta": "C"}]
    ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    vector_size = len(vectors[0])

    if not qdrant_tool._client.collection_exists(collection_name=collection_name):
        qdrant_tool._client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.DOT),
        )
    qdrant_tool.upsert_vectors(collection_name=collection_name, vectors=vectors, payloads=payloads, ids=ids)

    # Act: Search for a vector that is very close to the second vector
    query_vector = [0.8, 0.1, 0.2, 0.2]
    search_results = qdrant_tool.search_vectors(collection_name=collection_name, query_vector=query_vector, limit=3)

    # Assert: Verify the search results
    assert len(search_results) == 3
    # The first result should be the one with payload "B" as it's the closest
    assert search_results[0]["payload"]["meta"] == "B"
    # Check that scores are descending
    assert search_results[0]["score"] > search_results[1]["score"]
    assert search_results[1]["score"] > search_results[2]["score"]

    # Clean up
    qdrant_tool._client.delete_collection(collection_name=collection_name)


class TestAgent(AbstractAgent):
    def __init__(self, role: str, goal: str, backstory: str, llm: AbstractLLM, tools: list[AbstractTool]):
        self._role = role
        self._goal = goal
        self._backstory = backstory
        self._llm = llm
        self._tools = tools

    @property
    def role(self) -> str:
        return self._role

    @property
    def goal(self) -> str:
        return self._goal

    @property
    def backstory(self) -> str:
        return self._backstory

    @property
    def prompt_template(self) -> str | None:
        return None

    @property
    def tools(self) -> list[AbstractTool] | None:
        return self._tools

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None
    
    @property
    def llm(self) -> AbstractLLM | None:
        return self._llm

    @property
    def max_retries(self) -> int:
        return 3

class TestTask(AbstractTask):
    def __init__(self, description: str, expected_output: str, agent: AbstractAgent):
        self._description = description
        self._expected_output = expected_output
        self._agent = agent

    @property
    def description(self) -> str:
        return self._description

    @property
    def expected_output(self) -> str:
        return self._expected_output

    @property
    def agent(self) -> AbstractAgent:
        return self._agent
    
    @property
    def dependencies(self) -> list["AbstractTask"]:
        return []


@pytest.mark.integration
def test_agent_triggers_qdrant_tool(qdrant_tool, llm_factory):
    """
    Tests that a crewAI agent can be prompted to use the QdrantTool
    to perform an upsert operation.
    """
    # Arrange
    llm = CrewAILLM(llm_factory("ollama", "gemma2:2b"))
    
    agent = TestAgent(
        role="Vector Database Administrator",
        goal="Manage vector data in a Qdrant database.",
        backstory="An expert in vector databases.",
        llm=llm,
        tools=[qdrant_tool],
    )
    
    collection_name = f"test-agent-collection-{uuid.uuid4()}"
    vector_size = 4
    # The qdrant_tool doesn't create collections, so create it manually first.
    qdrant_tool._client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.DOT),
    )
    
    point_id = str(uuid.uuid4())
    task_prompt = f"""
    Your goal is to manage vector data in a Qdrant database using the "Qdrant VectorDB Tool".
    Execute the tool with the following parameters:
    - command: "upsert_vectors"
    - collection_name: '{collection_name}'
    - vectors: [[0.1, 0.2, 0.3, 0.4]]
    - payloads: [{{"source": "agent-test"}}]
    - ids: ["{point_id}"]
    """
    
    task = TestTask(
        description=task_prompt,
        expected_output="Confirmation of the upsert operation.",
        agent=agent,
    )
    
    orchestrator = CrewAIOrchestrator(config={"verbose": True})
    orchestrator.add_agent(agent)
    orchestrator.add_task(task)
    
    # Act
    orchestrator.execute()
    
    # Assert
    # Verify that the vector was inserted by the agent
    retrieved_points = qdrant_tool._client.retrieve(
        collection_name=collection_name,
        ids=[point_id],
        with_payload=True,
    )
    assert len(retrieved_points) == 1
    assert retrieved_points[0].id == point_id
    assert retrieved_points[0].payload == {"source": "agent-test"}
    
    # Clean up
    qdrant_tool._client.delete_collection(collection_name=collection_name)


if __name__ == "__main__":
    pytest.main([__file__])