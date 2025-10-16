import json
import os
from functools import cache
from pathlib import Path

import docker
import pytest
import requests
import structlog
from crewai import LLM
from testcontainers.core.container import DockerContainer as GenericContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

# Docker Host Configuration
# The following logic ensures that the DOCKER_HOST environment variable is set
# correctly, which is crucial for Docker-py and Testcontainers to connect to the
# Docker daemon. This is especially important on macOS where the Docker socket
# path can vary.

# Get a logger
log = structlog.get_logger()

if "DOCKER_HOST" not in os.environ:
    # For macOS, the Docker socket is typically located in the user's Library.
    # We construct the path and check for its existence.
    socket_path = Path("~/.docker/run/docker.sock").expanduser()

    if socket_path.exists():
        # If the socket exists, we set the DOCKER_HOST to point to it using the
        # 'unix://' scheme, which is understood by Docker-py.
        os.environ["DOCKER_HOST"] = f"unix://{socket_path}"
        log.debug(f"DOCKER_HOST set to: {os.environ['DOCKER_HOST']}")
    else:
        # As a fallback, for Linux or older Docker Desktop versions on macOS,
        # we check for the default Docker socket path.
        socket_path = Path("/var/run/docker.sock")
        if socket_path.exists():
            os.environ["DOCKER_HOST"] = f"unix://{socket_path}"
            log.debug(f"DOCKER_HOST set to: {os.environ['DOCKER_HOST']}")
        else:
            # If no Docker socket is found, we log a warning. This might lead
            # to connection errors if Docker is running but the socket is in a
            # non-standard location.
            log.warning("Could not find Docker socket.")


@pytest.fixture(scope="session")
def ollama_service():
    """
    A session-scoped fixture that starts, manages, and stops an
    Ollama Docker container for the entire test session.
    """
    log.debug("Setting up ollama_service fixture...")
    log.debug("Checking for Docker...")
    try:
        client = docker.from_env(timeout=5)
        client.ping()
        log.debug("Docker check passed.")
    except Exception as e:
        pytest.fail(f"Docker is not running or not installed. Failing integration tests. Error: {e}")

    log.debug("Creating Ollama container...")
    # Create a GenericContainer for the ollama/ollama image
    container = GenericContainer(image="ollama/ollama:latest")
    log.debug("Ollama container created.")

    # Expose the default Ollama port
    container.with_exposed_ports(11434)
    container.waiting_for(LogMessageWaitStrategy(r"Listening on \[::\]:11434").with_startup_timeout(120))

    log.debug("Starting Ollama container...")
    with container as ollama:
        log.debug("Ollama server is ready.")

        # Get the dynamically mapped host and port
        host = ollama.get_container_host_ip()
        port = ollama.get_exposed_port(11434)
        base_url = f"http://{host}:{port}"
        log.debug(f"Ollama service URL: {base_url}")

        yield base_url


@pytest.fixture(scope="session")
def llm_factory(ollama_service):
    """
    This fixture provides a factory to create LLM clients for different models.
    It also handles pulling the model if it's not already available.
    """
    log.debug("Setting up llm_factory fixture...")

    @cache
    def pull_model(model_name: str):
        """Pull the model using the REST API and cache the result."""
        log.debug(f"Pulling model: {model_name}...")
        pull_url = f"{ollama_service}/api/pull"
        try:
            response = requests.post(pull_url, json={"name": model_name}, stream=True)
            response.raise_for_status()

            # Wait for the pull to complete
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "error" in data:
                        raise Exception(f"Error pulling model: {data['error']}")
                    if data.get("status") == "success":
                        log.debug(f"Model {model_name} pulled successfully.")
                        return
            else:
                raise Exception(f"Model {model_name} not pulled successfully")
        except Exception as e:
            pytest.fail(f"Failed to pull model '{model_name}': {e}")

    def _factory(model_name: str):
        log.debug(f"Creating LLM for model: {model_name}...")
        pull_model(model_name)
        llm = LLM(model=f"ollama/{model_name}", base_url=ollama_service)
        log.debug(f"LLM for model {model_name} created.")
        return llm

    return _factory
