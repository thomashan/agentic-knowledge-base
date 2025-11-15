import hashlib
import json
import os
import subprocess
import time
import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from functools import cache
from pathlib import Path
from typing import Any

import pytest
import requests
import structlog
from crewai import LLM
from filelock import FileLock
from testcontainers.compose import DockerCompose
from testcontainers.core.container import DockerContainer as GenericContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

import docker


# Configure structlog for testing
@pytest.fixture(scope="session", autouse=True)
def configure_structlog():
    structlog.configure(
        processors=[
            structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


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


# Check if the local ollama models directory exists and mount it if it does
def __setup_ollama_model(container: GenericContainer = None):
    ollama_models_path = Path("~/.ollama/models").expanduser()
    if ollama_models_path.exists():
        log.debug(f"Found local Ollama models at {ollama_models_path}, mounting to container.")
        container.with_volume_mapping(str(ollama_models_path), "/root/.ollama", "rw")
    else:
        log.debug(f"Local Ollama models directory not found at {ollama_models_path}, creating it and mounting to container.")
        ollama_models_path.mkdir(parents=True, exist_ok=True)
        container.with_volume_mapping(str(ollama_models_path), "/root/.ollama", "rw")


@pytest.fixture(scope="session")
def ollama_service():
    """
    A session-scoped fixture that starts, manages, and stops an
    Ollama Docker container for the entire test session, or uses a local
    Ollama instance if available and/or running.
    """
    log.debug("Setting up ollama_service fixture...")

    ollama_base_url = "http://localhost:11434"
    ollama_process = None

    # Function to check if local Ollama server is ready
    def is_ollama_ready(url):
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
            return False

    # 1. Check if ollama command is available
    if subprocess.run(["which", "ollama"], capture_output=True).returncode == 0:
        log.debug("Local ollama command found.")

        # 2. Check if local ollama serve is already running
        if is_ollama_ready(ollama_base_url):
            log.debug("Local Ollama server is already running. Using existing instance.")
            yield ollama_base_url
            return
        else:
            log.debug("Local ollama command found, but server not running. Starting local ollama serve.")
            try:
                # Start ollama serve in the background
                ollama_process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                log.debug("Started 'ollama serve' in background.")

                # Wait for Ollama to be ready
                max_retries = 10
                for i in range(max_retries):
                    if is_ollama_ready(ollama_base_url):
                        log.debug("Local Ollama server is ready.")
                        break
                    log.debug(f"Waiting for local Ollama server to be ready (attempt {i + 1}/{max_retries})...")
                    time.sleep(2)  # Wait 2 seconds before retrying
                else:
                    pytest.fail("Local Ollama server did not become ready within the expected time.")

                yield ollama_base_url
            finally:
                if ollama_process:
                    log.debug("Terminating local ollama serve process.")
                    ollama_process.terminate()
                    ollama_process.wait(timeout=5)
                    if ollama_process.poll() is None:
                        ollama_process.kill()
                        ollama_process.wait()
    else:
        log.debug("Local ollama command not found. Falling back to Docker container.")
        log.debug("Checking for Docker...")
        try:
            client = docker.from_env(timeout=5)
            client.ping()
            log.debug("Docker check passed.")
        except Exception as e:
            pytest.fail(f"Docker is not running or not installed. Failing integration tests. Error: {e}")

        log.debug("Creating Ollama container...")
        # Create a GenericContainer for the ollama/ollama image
        container = GenericContainer(image="ollama/ollama:0.12.6")
        __setup_ollama_model(container)
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
        start_time = time.time()
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
                        end_time = time.time()
                        duration = end_time - start_time
                        log.debug(f"Model {model_name} pulled successfully in {duration:.2f} seconds.")
                        return
            else:
                raise Exception(f"Model {model_name} not pulled successfully")
        except Exception as e:
            pytest.fail(f"Failed to pull model '{model_name}': {e}")

    def _factory(model_name: str, timeout_s: int | float = 60, base_url: str = None):
        log.debug(f"Creating LLM for model: {model_name}...")
        pull_model(model_name)
        url = base_url or ollama_service
        log.debug(f"Using base_url: {url}, timeout_s: {timeout_s}s")
        llm = LLM(model=f"ollama/{model_name}", base_url=url, timeout=timeout_s)
        log.debug(f"LLM for model {model_name} created.")
        return llm

    return _factory


@pytest.fixture(scope="session")
def docker_compose_services(tmp_path_factory) -> Generator[dict[str, Any], None, None]:
    """
    A session-scoped fixture that starts, manages, and stops the Outline
    Docker Compose environment for the entire test session.
    This fixture is made compatible with pytest-xdist by ensuring the service
    is started only once using a file lock.
    """
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    compose_details_file = root_tmp_dir / "compose_details.json"
    lock_file = root_tmp_dir / "compose.lock"

    with FileLock(str(lock_file)):
        compose_file_path = Path(__file__).parent / "docker" / "outline_test_env"
        compose_instance = DockerCompose(
            compose_file_path,
            compose_file_name="docker-compose.yml",
            wait=True,
        )
        compose_instance.start()

        host = "localhost"
        port = compose_instance.get_service_port("outline", 3000)
        base_url = f"http://{host}:{port}"

        team_id, user_id, _collection_id = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
        api_key_secret = f"ol_api_{uuid.uuid4().hex}{uuid.uuid4().hex[:6]}"
        datetime.now(UTC).isoformat()
        hashed_secret = hashlib.sha256(api_key_secret.encode()).hexdigest()

        default_postgres_port = 5432
        pg_host = compose_instance.get_service_host("postgres", default_postgres_port)
        pg_port = compose_instance.get_service_port("postgres", default_postgres_port)
        db_url = f"postgresql://outline:password@{pg_host}:{pg_port}/outline"

        # Database seeding commands
        commands = [__outline_team_sql(team_id), __outline_user_sql(user_id, team_id), __outline_api_key_sql(api_key_secret, hashed_secret, user_id)]
        for cmd in commands:
            subprocess.run(["psql", db_url, "-c", cmd], check=True, capture_output=True)

        log.debug("Finished seeding database. Waiting for Outline to process new data...")
        time.sleep(5)

        details = {
            "outline_base_url": base_url,
            "api_key": api_key_secret,
            "db_url": db_url,
            "team_id": team_id,
            "user_id": user_id,
        }
        compose_details_file.write_text(json.dumps(details))

    details = json.loads(compose_details_file.read_text())
    yield details


@pytest.fixture
def outline_collection(docker_compose_services) -> Generator[str, None, None]:
    """
    A function-scoped fixture that creates a unique Outline collection for each
    test function, and provides the collection ID.
    """
    db_url = docker_compose_services["db_url"]
    team_id = docker_compose_services["team_id"]
    user_id = docker_compose_services["user_id"]
    collection_id = str(uuid.uuid4())

    commands = [
        __outline_collection_sql(collection_id, team_id),
        __outline_user_permission_sql(user_id, collection_id),
    ]
    for cmd in commands:
        subprocess.run(["psql", db_url, "-c", cmd], check=True, capture_output=True)

    yield collection_id


def __insert_into_sql(table_name: str, column_values: dict[str, str]) -> str:
    columns, values = __column_values_sql(column_values)
    statement = f'INSERT INTO "{table_name}" {columns} VALUES {values};'
    return statement


def __column_values_sql(column_values: dict[str, str]) -> tuple[str, str]:
    columns = '("' + '", "'.join(column_values.keys()) + '")'
    values = "('" + "', '".join(column_values.values()) + "')"
    return columns, values


def __outline_team_sql(team_id: str) -> str:
    return __insert_into_sql("teams", {"id": team_id, "name": f"Test Team {team_id}", "createdAt": "now()", "updatedAt": "now()"})


def __outline_user_sql(user_id: str, team_id: str) -> str:
    return __insert_into_sql(
        "users", {"id": user_id, "name": f"Test User {user_id}", "email": f"{user_id}@example.com", "teamId": team_id, "createdAt": "now()", "updatedAt": "now()", "role": "admin"}
    )


def __outline_api_key_sql(api_key_secret: str, hashed_secret: str, user_id: str) -> str:
    api_key_id = str(uuid.uuid4())
    return __insert_into_sql(
        "apiKeys", {"id": api_key_id, "name": f"Test API Key {api_key_id}", "secret": api_key_secret, "hash": hashed_secret, "userId": user_id, "createdAt": "now()", "updatedAt": "now()"}
    )


def __outline_collection_sql(collection_id: str, team_id: str) -> str:
    return __insert_into_sql("collections", {"id": collection_id, "name": f"Test Collection {collection_id}", "teamId": team_id, "createdAt": "now()", "updatedAt": "now()"})


def __outline_user_permission_sql(user_id: str, collection_id: str) -> str:
    return __insert_into_sql(
        "user_permissions", {"id": str(uuid.uuid4()), "userId": user_id, "collectionId": collection_id, "permission": "admin", "createdById": user_id, "createdAt": "now()", "updatedAt": "now()"}
    )
