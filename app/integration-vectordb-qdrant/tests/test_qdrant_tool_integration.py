import uuid
from typing import Any

import pytest
from agents_core.core import AbstractAgent, AbstractLLM, AbstractTask, AbstractTool
from crewai_adapter.adapter import CrewAILLM, CrewAIOrchestrator
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
    __test__ = False  # Instruct pytest to not collect this class

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
    __test__ = False  # Instruct pytest to not collect this class

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


def execute_qdrant_task(llm_source, qdrant_tool, task_description, expected_output):
    """Helper to execute a single Qdrant task with a fresh agent/orchestrator."""
    agent = TestAgent(
        role="Vector Database Administrator",
        goal="Manage vector data in a Qdrant database.",
        backstory="An expert in vector databases.",
        llm=llm_source,
        tools=[qdrant_tool],
    )

    task = TestTask(
        description=task_description,
        expected_output=expected_output,
        agent=agent,
    )

    orchestrator = CrewAIOrchestrator(config={"verbose": True})
    orchestrator.add_agent(agent)
    orchestrator.add_task(task)
    return orchestrator.execute()


@pytest.mark.integration
def test_agent_triggers_qdrant_tool(qdrant_tool, llm_factory):
    """
    Tests that a crewAI agent can be prompted to use the QdrantTool
    to create a collection, upsert a vector, and then search for it.
    """
    # Arrange
    crew_ai_llm = CrewAILLM(llm_factory())
    collection_name = f"test-agent-collection-{uuid.uuid4()}"
    point_id = str(uuid.uuid4())

    # --- Step 1: Create Collection ---
    create_task_prompt = f"""
    Create a new collection in Qdrant with the name '{collection_name}'.
    Use the 'Qdrant VectorDB Tool' with the 'create_collection' command.

    REQUIRED Arguments:
    {{
        "command": "create_collection",
        "collection_name": "{collection_name}",
        "vector_size": 4,
        "distance": "Dot"
    }}
    NOTE: 'vector_size' MUST be exactly 4. 'distance' MUST be "Dot".
    """

    execute_qdrant_task(crew_ai_llm, qdrant_tool, create_task_prompt, "Confirmation that the collection was created.")

    # Assert Collection Created
    assert qdrant_tool._client.collection_exists(collection_name)

    # --- Step 1.5: List Collections ---
    agent_list = TestAgent(
        role="Vector Database Administrator",
        goal="Manage vector data in a Qdrant database.",
        backstory="An expert in vector databases.",
        llm=CrewAILLM(llm_factory()),
        tools=[qdrant_tool],
    )

    list_task_prompt = """
    List all collections in the Qdrant database.
    Use the 'Qdrant VectorDB Tool' with the 'list_collections' command.

    REQUIRED Arguments:
    {
        "command": "list_collections"
    }
    """

    list_task = TestTask(
        description=list_task_prompt,
        expected_output="A list of collection names.",
        agent=agent_list,
    )

    orchestrator_list = CrewAIOrchestrator(config={"verbose": True})
    orchestrator_list.add_agent(agent_list)
    orchestrator_list.add_task(list_task)
    list_result = orchestrator_list.execute()

    # Assert Collection is listed
    assert collection_name in list_result.raw_output

    # --- Step 2: Upsert Vector ---
    upsert_task_prompt = f"""
    Add a vector to the '{collection_name}' collection.
    The collection '{collection_name}' ALREADY EXISTS. DO NOT create it.
    Use the 'Qdrant VectorDB Tool' with the 'upsert_vectors' command.

    REQUIRED Arguments:
    {{
        "command": "upsert_vectors",
        "collection_name": "{collection_name}",
        "vectors": [[0.1, 0.2, 0.3, 0.4]],
        "payloads": [{{"source": "agent-test"}}],
        "ids": ["{point_id}"]
    }}
    """

    execute_qdrant_task(crew_ai_llm, qdrant_tool, upsert_task_prompt, "Confirmation of the upsert operation.")

    # Assert Vector Inserted
    retrieved_points = qdrant_tool._client.retrieve(
        collection_name=collection_name,
        ids=[point_id],
        with_payload=True,
    )
    assert len(retrieved_points) == 1
    assert retrieved_points[0].id == point_id
    assert retrieved_points[0].payload == {"source": "agent-test"}

    # --- Step 3: Search Vector ---
    search_task_prompt = f"""
    Search for the vector in the '{collection_name}' collection.
    Use the 'Qdrant VectorDB Tool' with the 'search_vectors' command.

    The EXACT input for the 'query_vector' argument should be: [0.1, 0.2, 0.3, 0.4].

    REQUIRED Arguments:
    {{
        "collection_name": "{collection_name}",
        "query_vector": [0.1, 0.2, 0.3, 0.4],
        "limit": 1
    }}

    """

    search_result = execute_qdrant_task(crew_ai_llm, qdrant_tool, search_task_prompt, "The ID and payload of the found vector.")

    # Assert Search Found ID
    assert point_id in search_result.raw_output

    # --- Step 4: Delete Vector ---
    delete_task_prompt = f"""
    DELETE the vector with ID "{point_id}" from the '{collection_name}' collection.
    You MUST use the 'Qdrant VectorDB Tool' with the 'delete_vectors' command.
    DO NOT SEARCH OR USE ANY OTHER COMMAND. DELETE ONLY.
    The collection name is '{collection_name}' and the ID to delete is '{point_id}'.
    """

    execute_qdrant_task(crew_ai_llm, qdrant_tool, delete_task_prompt, "Confirmation that the vector was deleted.")

    # Assert Vector Deleted
    retrieved_points = qdrant_tool._client.retrieve(
        collection_name=collection_name,
        ids=[point_id],
        with_payload=True,
    )
    assert len(retrieved_points) == 0

    # Clean up
    qdrant_tool._client.delete_collection(collection_name=collection_name)


@pytest.mark.integration
def test_create_collection_integration(qdrant_tool):
    """
    Tests that the create_collection method successfully creates a new collection.
    """
    # Arrange
    collection_name = f"test_create_{uuid.uuid4()}"
    vector_size = 128
    distance = "Dot"

    # Act
    result = qdrant_tool.create_collection(collection_name=collection_name, vector_size=vector_size, distance=distance)

    # Assert
    assert f"Collection '{collection_name}' created successfully." == result
    assert qdrant_tool._client.collection_exists(collection_name=collection_name)

    # Clean up
    qdrant_tool._client.delete_collection(collection_name=collection_name)


@pytest.mark.integration
def test_list_collections_integration(qdrant_tool):
    """
    Tests that the list_collections method correctly returns a list of existing collections.
    """
    # Arrange
    collection_name1 = f"test_list_1_{uuid.uuid4()}"
    collection_name2 = f"test_list_2_{uuid.uuid4()}"
    vector_size = 4
    distance = "Cosine"

    qdrant_tool.create_collection(collection_name=collection_name1, vector_size=vector_size, distance=distance)
    qdrant_tool.create_collection(collection_name=collection_name2, vector_size=vector_size, distance=distance)

    # Act
    collections = qdrant_tool.list_collections()

    # Assert
    assert collection_name1 in collections
    assert collection_name2 in collections
    assert len(collections) >= 2  # There might be other test collections

    # Clean up
    qdrant_tool._client.delete_collection(collection_name=collection_name1)
    qdrant_tool._client.delete_collection(collection_name=collection_name2)


@pytest.mark.integration
def test_get_collection_info_integration(qdrant_tool):
    """
    Tests that the get_collection_info method retrieves correct details about a collection.
    """
    # Arrange
    collection_name = f"test_info_{uuid.uuid4()}"
    vector_size = 768
    distance = "Euclid"

    qdrant_tool.create_collection(collection_name=collection_name, vector_size=vector_size, distance=distance)

    # Act
    info = qdrant_tool.get_collection_info(collection_name=collection_name)

    # Assert
    assert info["status"] == "green"
    assert info["vector_size"] == vector_size
    assert info["distance"] == distance
    assert "points_count" in info

    # Clean up
    qdrant_tool._client.delete_collection(collection_name=collection_name)


@pytest.mark.integration
def test_delete_collection_integration(qdrant_tool):
    """
    Tests that the delete_collection method successfully removes a collection.
    """
    # Arrange
    collection_name = f"test_delete_coll_{uuid.uuid4()}"
    vector_size = 42
    distance = "Cosine"

    qdrant_tool.create_collection(collection_name=collection_name, vector_size=vector_size, distance=distance)
    assert qdrant_tool._client.collection_exists(collection_name=collection_name)

    # Act
    result = qdrant_tool.delete_collection(collection_name=collection_name)

    # Assert
    assert f"Collection '{collection_name}' deleted successfully." == result
    assert not qdrant_tool._client.collection_exists(collection_name=collection_name)


if __name__ == "__main__":
    pytest.main([__file__])
