import uuid

import pytest
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


if __name__ == "__main__":
    pytest.main()
