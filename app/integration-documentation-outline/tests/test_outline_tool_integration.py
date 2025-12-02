import time

import pytest
from documentation.outline_tool import OutlineTool


@pytest.fixture
def outline_tool(docker_compose_services, outline_collection):
    """
    A fixture that provides an instance of the OutlineTool, configured to
    connect to the Outline service running in the Docker Compose environment.
    """
    base_url = docker_compose_services["outline_base_url"]
    api_key = docker_compose_services["api_key"]
    collection_id = outline_collection
    return OutlineTool(api_key=api_key, base_url=base_url, collection_id=collection_id)


def title_to_url_slug(title: str) -> str:
    return "-".join(title.lower().split(" ")).replace(".", "")


@pytest.mark.integration
def test_create_or_update_document(outline_tool):
    """
    Tests creating and updating a document in a real Outline instance.
    """
    title = f"Test Create-Update {time.time()}"
    initial_content = "This is the initial content of the test document."
    updated_content = "This is the updated content of the test document."

    # Create the document
    response = outline_tool.create_or_update_document(title=title, content=initial_content)
    assert response is not None
    assert response["data"]["title"] == title
    assert initial_content in response["data"]["text"]
    # Verify the URL is a partial URL derived from the document title
    created_url = response["data"]["url"]
    expected_slug_part = title_to_url_slug(title)
    assert expected_slug_part in created_url

    # Update the document
    response = outline_tool.create_or_update_document(title=title, content=updated_content)
    assert response is not None
    assert response["data"]["title"] == title
    assert updated_content in response["data"]["text"]
    assert response["data"]["id"] == response["data"]["id"]
    # Verify the URL is still the same
    updated_url = response["data"]["url"]
    assert updated_url == created_url


@pytest.mark.integration
def test_publish_and_get_document(outline_tool):
    """
    Tests publishing a new document and then retrieving it.
    """
    title = f"Test Publish-Get {time.time()}"
    content = "Content for publish and get test."

    # 1. Publish document
    response = outline_tool.publish_document(title=title, content=content)
    assert response is not None
    assert response["data"]["title"] == title
    assert content in response["data"]["text"]
    doc_id = response["data"]["id"]
    # Verify the URL is a partial URL derived from the document title
    created_url = response["data"]["url"]
    expected_slug_part = title_to_url_slug(title)
    assert expected_slug_part in created_url

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
    response = outline_tool.update_document(doc_id, new_title, new_content)
    assert response is not None
    assert response["data"]["id"] == doc_id
    assert response["data"]["title"] == new_title
    assert new_content in response["data"]["text"]

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
    response = outline_tool.publish_document(title=title, content=content)
    doc_id = response["data"]["id"]

    # 2. Get the new document and verify its initial state
    response = outline_tool.get_document(doc_id)
    assert response["data"]["archivedAt"] is None
    assert response["data"]["deletedAt"] is None

    # 3. Delete the document (soft delete)
    response = outline_tool.delete_document(doc_id, permanent=False)
    assert response is True

    # 4. Get the document again and verify it has been soft-deleted
    response = outline_tool.get_document(doc_id)
    assert response is not None
    assert response["data"]["deletedAt"] is not None


if __name__ == "__main__":
    pytest.main([__file__])
