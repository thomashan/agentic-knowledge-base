import hashlib
import json
import os
import subprocess
import time
import uuid
from datetime import UTC, datetime
from functools import cache
from pathlib import Path

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


def _is_ollama_ready(url):
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        return False


def _start_local_ollama():
    log.debug("Starting local ollama serve.")
    try:
        ollama_process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(10):
            if _is_ollama_ready("http://localhost:11434"):
                return "http://localhost:11434", ollama_process
            time.sleep(2)
        pytest.fail("Local Ollama server did not become ready.")
    except Exception as e:
        pytest.fail(f"Failed to start local Ollama server: {e}")


def _start_docker_ollama():
    log.debug("Local ollama command not found. Falling back to Docker container.")
    try:
        client = docker.from_env(timeout=5)
        client.ping()
    except Exception as e:
        pytest.fail(f"Docker is not running or not installed. Error: {e}")

    container = GenericContainer(image="ollama/ollama:0.12.6")
    __setup_ollama_model(container)
    container.with_exposed_ports(11434)
    container.waiting_for(LogMessageWaitStrategy(r"Listening on \[::\]:11434").with_startup_timeout(120))
    container.start()
    host = container.get_container_host_ip()
    port = container.get_exposed_port(11434)
    return f"http://{host}:{port}", container


@pytest.fixture(scope="session")
def ollama_service(tmp_path_factory, worker_id):
    """
    A session-scoped fixture that starts, manages, and stops an
    Ollama Docker container for the entire test session, or uses a local
    Ollama instance if available and/or running.
    This fixture is made compatible with pytest-xdist by ensuring the service
    is started only once using a file lock.
    """
    log.debug(f"Worker {worker_id}: Setting up ollama_service fixture...")
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    ollama_url_file = root_tmp_dir / "ollama_url.txt"
    lock_file = root_tmp_dir / "ollama.lock"

    with FileLock(str(lock_file)):
        log.debug(f"Worker {worker_id}: Acquired lock for ollama_service.")
        if ollama_url_file.is_file():
            ollama_base_url = ollama_url_file.read_text().strip()
            log.debug(f"Worker {worker_id}: Ollama URL already exists: {ollama_base_url}")
        else:
            log.debug(f"Worker {worker_id}: Ollama URL file not found. This worker will start the service.")
            ollama_process, container = None, None
            if subprocess.run(["which", "ollama"], capture_output=True).returncode == 0:
                log.debug("Local ollama command found.")
                if _is_ollama_ready("http://localhost:11434"):
                    log.debug("Local Ollama server is already running. Using existing instance.")
                    ollama_base_url = "http://localhost:11434"
                else:
                    ollama_base_url, ollama_process = _start_local_ollama()
            else:
                ollama_base_url, container = _start_docker_ollama()

            ollama_url_file.write_text(ollama_base_url)
            log.debug(f"Worker {worker_id}: Wrote Ollama URL to file: {ollama_base_url}")

            # Store service details for teardown
            service_info = {
                "url": ollama_base_url,
                "process_pid": ollama_process.pid if ollama_process else None,
                "container_id": container.get_wrapped_container().id if container else None,
            }
            (root_tmp_dir / "ollama_service_info.json").write_text(json.dumps(service_info))

    ollama_base_url = ollama_url_file.read_text().strip()
    yield ollama_base_url

    # Teardown logic, executed only by the master worker
    if worker_id == "master":
        log.debug("Master worker tearing down Ollama service.")
        service_info_file = root_tmp_dir / "ollama_service_info.json"
        if service_info_file.is_file():
            with FileLock(str(lock_file)):
                service_info = json.loads(service_info_file.read_text())
                if service_info.get("process_pid"):
                    try:
                        os.kill(service_info["process_pid"], 15)  # SIGTERM
                        log.debug(f"Terminated ollama process with PID {service_info['process_pid']}.")
                    except ProcessLookupError:
                        log.debug(f"Ollama process with PID {service_info['process_pid']} not found.")
                if service_info.get("container_id"):
                    try:
                        client = docker.from_env()
                        container = client.containers.get(service_info["container_id"])
                        container.stop()
                        container.remove()
                        log.debug(f"Stopped and removed Ollama container {service_info['container_id']}.")
                    except docker.errors.NotFound:
                        log.debug(f"Ollama container {service_info['container_id']} not found.")
                # Clean up control files
                service_info_file.unlink()
                ollama_url_file.unlink()


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
            # Use a longer timeout for the initial connection to the pull endpoint
            with requests.post(pull_url, json={"name": model_name}, stream=True, timeout=30) as response:
                response.raise_for_status()
                # Process the streaming response
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
                    # This part is reached if the stream ends without a 'success' status
                    raise Exception(f"Stream for model pull of {model_name} ended without success status.")
        except requests.exceptions.ReadTimeout:
            pytest.fail(f"Failed to pull model '{model_name}': The request timed out after waiting for the stream to start.")
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


@pytest.fixture
def unique_id():
    """
    A function-scoped fixture that provides a unique ID for each test function,
    useful for creating isolated resources in parallel test runs.
    """
    return f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def docker_compose_services(tmp_path_factory, worker_id):
    """
    A session-scoped fixture that starts, manages, and stops the Outline
    Docker Compose environment for the entire test session.
    This fixture is made compatible with pytest-xdist by ensuring the service
    is started only once using a file lock.
    """
    log.debug(f"Worker {worker_id}: Setting up docker_compose_services fixture...")
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    compose_details_file = root_tmp_dir / "compose_details.json"
    lock_file = root_tmp_dir / "compose.lock"

    with FileLock(str(lock_file)):
        log.debug(f"Worker {worker_id}: Acquired lock for docker_compose_services.")
        if compose_details_file.is_file():
            details = json.loads(compose_details_file.read_text())
            log.debug(f"Worker {worker_id}: Docker Compose details already exist: {details}")
        else:
            log.debug(f"Worker {worker_id}: Docker Compose details not found. This worker will start the services.")
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

            team_id, user_id, collection_id = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
            api_key_secret = f"ol_api_{uuid.uuid4().hex}{uuid.uuid4().hex[:6]}"
            now = datetime.now(UTC).isoformat()
            hashed_secret = hashlib.sha256(api_key_secret.encode()).hexdigest()

            pg_host = compose_instance.get_service_host("postgres", 5432)
            pg_port = compose_instance.get_service_port("postgres", 5432)
            db_url = f"postgresql://outline:password@{pg_host}:{pg_port}/outline"

            # Database seeding commands
            commands = [
                f"INSERT INTO teams (id, name, \"createdAt\", \"updatedAt\") VALUES ('{team_id}', 'Test Team', '{now}', '{now}');",
                f"INSERT INTO users (id, name, email, \"teamId\", \"createdAt\", \"updatedAt\", role) VALUES ('{user_id}', 'Test User', 'test@example.com', '{team_id}', '{now}', '{now}', 'admin');",
                f"INSERT INTO collections (id, name, \"teamId\", \"createdAt\", \"updatedAt\") VALUES ('{collection_id}', 'Test Collection', '{team_id}', '{now}', '{now}');",
                (
                    f'INSERT INTO "apiKeys" (id, name, secret, hash, "userId", "createdAt", "updatedAt") '
                    f"VALUES ('{str(uuid.uuid4())}', 'Test API Key', '{api_key_secret}', "
                    f"'{hashed_secret}', '{user_id}', '{now}', '{now}');"
                ),
                (
                    f'INSERT INTO user_permissions (id, "userId", "collectionId", permission, "createdById", "createdAt", "updatedAt") '
                    f"VALUES ('{str(uuid.uuid4())}', '{user_id}', '{collection_id}', "
                    f"'admin', '{user_id}', '{now}', '{now}');"
                ),
            ]
            for cmd in commands:
                subprocess.run(["psql", db_url, "-c", cmd], check=True, capture_output=True)

            log.debug("Finished seeding database. Waiting for Outline to process new data...")
            time.sleep(5)

            details = {
                "outline_base_url": base_url,
                "api_key": api_key_secret,
                "collection_id": collection_id,
                "db_url": db_url,
                "team_id": team_id,
                "user_id": user_id,
            }
            compose_details_file.write_text(json.dumps(details))
            log.debug(f"Worker {worker_id}: Wrote Docker Compose details to file: {details}")

    details = json.loads(compose_details_file.read_text())
    yield details

    if worker_id == "master":
        log.debug("Master worker tearing down Docker Compose services.")
        if compose_details_file.is_file():
            with FileLock(str(lock_file)):
                # Re-instantiate DockerCompose to stop the services
                compose_file_path = Path(__file__).parent / "docker" / "outline_test_env"
                compose = DockerCompose(compose_file_path, compose_file_name="docker-compose.yml")
                compose.stop()
                log.debug("Stopped Docker Compose services.")
                # Clean up control file
                compose_details_file.unlink(missing_ok=True)


@pytest.fixture
def outline_collection(docker_compose_services):
    """
    A function-scoped fixture that creates a unique Outline collection for each
    test function, and provides the collection ID.
    """
    db_url = docker_compose_services["db_url"]
    team_id = docker_compose_services["team_id"]
    user_id = docker_compose_services["user_id"]
    now = datetime.now(UTC).isoformat()
    collection_id = str(uuid.uuid4())

    command = f"INSERT INTO collections (id, name, \"teamId\", \"createdAt\", \"updatedAt\") VALUES ('{collection_id}', 'Test Collection {collection_id}', '{team_id}', '{now}', '{now}');"
    subprocess.run(["psql", db_url, "-c", command], check=True, capture_output=True)

    permission_command = (
        f'INSERT INTO user_permissions (id, "userId", "collectionId", permission, "createdById", "createdAt", "updatedAt") '
        f"VALUES ('{str(uuid.uuid4())}', '{user_id}', '{collection_id}', 'admin', '{user_id}', '{now}', '{now}');"
    )
    subprocess.run(["psql", db_url, "-c", permission_command], check=True, capture_output=True)

    yield collection_id
