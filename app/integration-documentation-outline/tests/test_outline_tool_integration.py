import time

import pytest
from documentation.outline_tool import OutlineTool


@pytest.fixture(scope="module")
def outline_tool(docker_compose_services):
    """
    A fixture that provides an instance of the OutlineTool, configured to
    connect to the Outline service running in the Docker Compose environment.
    """
    base_url = docker_compose_services["outline_base_url"]
    api_key = docker_compose_services["api_key"]
    collection_id = docker_compose_services["collection_id"]
    return OutlineTool(api_key=api_key, base_url=base_url, collection_id=collection_id)


@pytest.mark.integration
def test_create_and_update_document_with_real_outline(outline_tool):
    """
    Tests creating and updating a document in a real Outline instance.
    """
    title = f"Test Create-Update {time.time()}"
    initial_content = "This is the initial content of the test document."
    updated_content = "This is the updated content of the test document."

    # Create the document
    created_document = outline_tool.create_or_update_document(title=title, content=initial_content)
    assert created_document is not None
    assert created_document["data"]["title"] == title
    assert initial_content in created_document["data"]["text"]

    # Update the document
    updated_document = outline_tool.create_or_update_document(title=title, content=updated_content)
    assert updated_document is not None
    assert updated_document["data"]["title"] == title
    assert updated_content in updated_document["data"]["text"]
    assert updated_document["data"]["id"] == created_document["data"]["id"]


@pytest.mark.integration
def test_publish_and_get_document(outline_tool):
    """
    Tests publishing a new document and then retrieving it.
    """
    title = f"Test Publish-Get {time.time()}"
    content = "Content for publish and get test."

    # 1. Publish document
    published_document = outline_tool.publish_document(title=title, content=content)
    assert published_document is not None
    assert published_document["data"]["title"] == title
    assert content in published_document["data"]["text"]
    doc_id = published_document["data"]["id"]

    # 2. Get document
    retrieved_document = outline_tool.get_document(doc_id)
    assert retrieved_document is not None
    assert retrieved_document["data"]["id"] == doc_id
    assert retrieved_document["data"]["title"] == title
    assert content in retrieved_document["data"]["text"]


@pytest.mark.integration
def test_update_document(outline_tool):
    """
    Tests updating a document's title and content.
    """
    title = f"Test Update {time.time()}"
    content = "Initial content for update test."
    published_document = outline_tool.publish_document(title=title, content=content)
    doc_id = published_document["data"]["id"]

    new_title = f"Test Updated Title {time.time()}"
    new_content = "This is the new, updated content."

    # Update the document
    updated_document = outline_tool.update_document(doc_id, new_title, new_content)
    assert updated_document is not None
    assert updated_document["data"]["id"] == doc_id
    assert updated_document["data"]["title"] == new_title
    assert new_content in updated_document["data"]["text"]

    # Verify by getting the document again
    retrieved_document = outline_tool.get_document(doc_id)
    assert retrieved_document["data"]["title"] == new_title
    assert new_content in retrieved_document["data"]["text"]


@pytest.mark.integration
def test_delete_document(outline_tool):
    """
    Tests soft-deleting a document and verifying its status.
    """
    title = f"Test Delete {time.time()}"
    content = "This document will be soft-deleted."

    # 1. Create the document
    published_document = outline_tool.publish_document(title=title, content=content)
    doc_id = published_document["data"]["id"]

    # 2. Get the new document and verify its initial state
    retrieved_before_delete = outline_tool.get_document(doc_id)
    assert retrieved_before_delete["data"]["archivedAt"] is None
    assert retrieved_before_delete["data"]["deletedAt"] is None

    # 3. Delete the document (soft delete)
    delete_result = outline_tool.delete_document(doc_id, permanent=False)
    assert delete_result is True

    # 4. Get the document again and verify it has been soft-deleted
    retrieved_after_delete = outline_tool.get_document(doc_id)
    assert retrieved_after_delete is not None
    assert retrieved_after_delete["data"]["deletedAt"] is not None
