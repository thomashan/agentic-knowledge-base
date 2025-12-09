import hashlib
import json
import os
import subprocess
import time
import uuid
from collections.abc import Callable, Generator
from os import PathLike
from pathlib import Path
from typing import Any

import pytest
import requests
import structlog
from agents_core.core import AbstractLLM
from crewai import LLM
from dotenv import load_dotenv
from filelock import FileLock
from integration_llm.factory import create_llm
from testcontainers.compose import DockerCompose
from testcontainers.core.container import DockerContainer
from testcontainers.core.container import DockerContainer as GenericContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.qdrant import QdrantContainer
from vectordb.qdrant_tool import QdrantTool

import docker


@pytest.fixture(scope="session", autouse=True)
def load_test_environment():
    """
    Load environment variables from .test.env (or .ci.test.env if in CI)
    file before the test session starts.
    This fixture runs automatically for every test session.
    """
    is_ci = os.getenv("CI") == "true"
    if is_ci:
        dotenv_filename = ".ci.test.env"
        log.info(f"CI environment detected. Attempting to load environment variables from {dotenv_filename}...")
    else:
        dotenv_filename = ".test.env"
        log.info(f"Local environment detected. Attempting to load environment variables from {dotenv_filename}...")

    # Assuming conftest.py is in the project root.
    dotenv_path = Path(__file__).parent / dotenv_filename

    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
        log.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        log.warning(f"{dotenv_filename} file not found at {dotenv_path}. Skipping dedicated test environment loading.")


# Configure structlog for testing
@pytest.fixture(scope="session", autouse=True)
def configure_structlog(request):
    original_log_file = request.config.getoption("--log-file")
    log_file = original_log_file + ".jsonl" if original_log_file else None
    if log_file:
        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            logger_factory=structlog.PrintLoggerFactory(file=Path.open(log_file, "a")),
            cache_logger_on_first_use=False,
        )
    else:
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
default_ollam_url = "http://localhost:11434"

if "DOCKER_HOST" not in os.environ:
    # For macOS, the Docker socket is typically located in the user's Library.
    # We construct the path and check for its existence.
    socket_path = Path("~/.docker/run/docker.sock").expanduser()

    if socket_path.exists():
        # If the socket exists, we set the DOCKER_HOST to point to it using the
        # 'unix://' scheme, which is understood by Docker-py.
        os.environ["DOCKER_HOST"] = f"unix://{socket_path}"
        log.info(f"DOCKER_HOST set to: {os.environ['DOCKER_HOST']}")
    else:
        # As a fallback, for Linux or older Docker Desktop versions on macOS,
        # we check for the default Docker socket path.
        socket_path = Path("/var/run/docker.sock")
        if socket_path.exists():
            os.environ["DOCKER_HOST"] = f"unix://{socket_path}"
            log.info(f"DOCKER_HOST set to: {os.environ['DOCKER_HOST']}")
        else:
            # If no Docker socket is found, we log a warning. This might lead
            # to connection errors if Docker is running but the socket is in a
            # non-standard location.
            log.warning("Could not find Docker socket.")


# Check if the local ollama models directory exists and mount it if it does
def __setup_ollama_model(container: GenericContainer = None):
    ollama_models_path = Path("~/.ollama/models").expanduser()
    if ollama_models_path.exists():
        log.info(f"Found local Ollama models at {ollama_models_path}, mounting to container.")
        container.with_volume_mapping(str(ollama_models_path), "/root/.ollama", "rw")
    else:
        log.info(f"Local Ollama models directory not found at {ollama_models_path}, creating it and mounting to container.")
        ollama_models_path.mkdir(parents=True, exist_ok=True)
        container.with_volume_mapping(str(ollama_models_path), "/root/.ollama", "rw")


def __temp_file(tmp_path_factory, file_name) -> Path:
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    return root_tmp_dir / file_name


def __read_service_file(tmp_path_factory, file_name) -> dict[str, Any]:
    file = __temp_file(tmp_path_factory, file_name)
    if file.is_file():
        return json.loads(file.read_text())
    else:
        return {}


def __write_service_file(tmp_path_factory, file_name, details: dict[str, Any]):
    file = __temp_file(tmp_path_factory, file_name)
    if not file.is_file():
        return file.write_text(json.dumps(details))
    return None


# Function to check if local Ollama server is ready
def __is_ollama_ready(url):
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except Exception as ex:
        log.info(f"Failed to get Ollama tags. Error: {ex}")
        return False


def __use_native_ollama():
    log.info("Local ollama command found.")

    ollama_base_url = default_ollam_url
    # 2. Check if local ollama serve is already running
    if __is_ollama_ready(ollama_base_url):
        log.info("Local Ollama server is already running. Using existing instance.")
    else:
        log.info("Local ollama command found, but server not running. Starting local ollama serve.")
        # Start ollama serve in the background
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.info("Started 'ollama serve' in background.")

        # Wait for Ollama to be ready
        max_retries = 10
        for i in range(max_retries):
            if __is_ollama_ready(ollama_base_url):
                log.info("Local Ollama server is ready.")
                break
            log.info(f"Waiting for local Ollama server to be ready (attempt {i + 1}/{max_retries})...")
            time.sleep(2)  # Wait 2 seconds before retrying
        else:
            pytest.fail("Local Ollama server did not become ready within the expected time.")
    return ollama_base_url


def __is_docker_present():
    try:
        client = docker.from_env(timeout=5)
        client.ping()
        log.info("Docker check passed.")
        return True
    except Exception as ex:
        log.info(f"Failed to get docker client. Error: {ex}")
        return False


def __is_ollama_command_present():
    return subprocess.run(["which", "ollama"], capture_output=True).returncode == 0


@pytest.fixture(scope="session")
def ollama_service(tmp_path_factory, worker_id) -> Generator[dict[str, Any], None, None]:
    """
    A session-scoped fixture that starts, manages, and stops an
    Ollama Docker container for the entire test session, or uses a local
    Ollama instance if available and/or running.
    """
    log.info(f"Setting up ollama_service fixture in work_id: {worker_id}...")

    # If native ollama command is present, use it and bypass docker management.
    if __is_ollama_command_present():
        base_url = __use_native_ollama()
        yield {"base_url": base_url}
        return

    # --- Docker Path ---
    # If native ollama is not present, use the generic docker container helper.

    def container_supplier() -> DockerContainer:
        """Supplies a configured Ollama container."""
        ollama_default_port = 11434
        container = GenericContainer(
            image="ollama/ollama:0.13.0",
            _wait_strategy=LogMessageWaitStrategy(r"Listening on \[::\]:"),
            ports=[ollama_default_port],
        )
        __setup_ollama_model(container)
        return container

    def service_file_writer(ollama_container: GenericContainer) -> dict[str, Any]:
        """Writes the service details from the container."""
        ollama_default_port = 11434
        host = ollama_container.get_container_host_ip()
        port = ollama_container.get_exposed_port(ollama_default_port)
        log.info(f"Ollama container started. Service URL: http://{host}:{port}")
        return {"base_url": f"http://{host}:{port}"}

    yield from __start_docker_container(
        tmp_path_factory,
        "ollama_service",
        container_supplier,
        service_file_writer,
        worker_id,
    )


def _pull_ollama_model(tmp_path_factory, base_url: str, model_name: str):
    log.info(f"Pulling ollama model: {model_name} from {base_url}...")
    lock_file = __temp_file(tmp_path_factory, "ollama_model.json.lock")
    model_name = model_name.replace("ollama/", "")
    ollama_models = __read_service_file(tmp_path_factory, "ollama_model.json")
    models: set[str] = set(ollama_models.get("models", []))
    log.info(f"known Ollama models: {models}")

    with FileLock(lock_file):
        if model_name not in models:
            """Pull the model using the REST API and cache the result."""
            log.info(f"Pulling model: {model_name}...")
            pull_url = f"{base_url}/api/pull"
            log.info(f"pull_url: {pull_url}")
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
                            log.info(f"Model {model_name} pulled successfully in {duration:.2f} seconds.")
                            models.add(model_name)
                            ollama_models["models"] = list(models)
                            __write_service_file(tmp_path_factory, "ollama_model.json", ollama_models)
                            return
                else:
                    raise Exception(f"Model {model_name} not pulled successfully")
            except Exception as e:
                log.info(f"Failed to pull model '{model_name}' calling {pull_url}: {e}")
                pytest.fail(f"Failed to pull model '{model_name}': {e}")


def _ollama_url(url: str, ollama_service: dict[str, Any]) -> str:
    return ollama_service["base_url"] if url == default_ollam_url else url


def _check_mandatory_env_vars(parameter: Any, env_var: str, env_var_default_value: str | None = None) -> Any:
    returned_valued = parameter or os.getenv(env_var, env_var_default_value)
    if not returned_valued:
        raise ValueError(f"{env_var} must be set in the environment or passed as arguments.")
    return returned_valued


@pytest.fixture(scope="session")
def llm_factory(request, tmp_path_factory):
    def _factory(
        provider: str | None = None,
        model_name: str | None = None,
        timeout_s: int | float = 300,
        base_url: str | None = None,
        **kwargs,
    ) -> LLM:
        provider = _check_mandatory_env_vars(provider, "LLM_PROVIDER", "ollama")
        model_name = _check_mandatory_env_vars(model_name, "LLM_MODEL", "gemma2:2b")
        base_url = _check_mandatory_env_vars(base_url, "LLM_BASE_URL", default_ollam_url)
        log.info(f"Setting up llm_factory fixture... provider: {provider}, model_name: {model_name}, base_url: {base_url}")
        full_model_name = f"{provider}/{model_name}"

        if provider == "ollama":
            dynamic_ollama_service = request.getfixturevalue("ollama_service")
            ollama_base_url = _ollama_url(base_url, dynamic_ollama_service)
            if base_url != default_ollam_url and ollama_base_url != base_url:
                raise Exception(f"LLM_BASE_URL: {base_url} does not match ollama_service base_url: {ollama_base_url}.")
            _pull_ollama_model(tmp_path_factory, ollama_base_url, model_name)
            base_url = ollama_base_url

        # The create_llm function handles the actual instantiation
        abstract_llm: AbstractLLM = create_llm(
            provider=provider,
            model=full_model_name,
            base_url=base_url,
            timeout_s=timeout_s,
            **kwargs,
        )

        log.info(f"LLM for provider: {provider}, model_name: {model_name} created.")
        return abstract_llm.llm()

    return _factory


def __start_docker_compose(
    tmp_path_factory: pytest.TempPathFactory,
    service_file_name: str,
    context: PathLike[str],
    compose_file_name: str,
    service_details_supplier: Callable[[DockerCompose], dict[str, Any]],
    worker_id: str,
) -> Generator[dict[str, Any], None, None]:
    log.info(f"Setting up docker compose fixture {service_file_name} with {context}/{compose_file_name} ...", worker_id=worker_id)
    service_file = __temp_file(tmp_path_factory, f"{service_file_name}.json")
    lock_file = __temp_file(tmp_path_factory, f"{service_file_name}.lock")
    worker_count_file = __temp_file(tmp_path_factory, f"{service_file_name}.count")

    with FileLock(str(lock_file)):
        worker_count_file.write_text(f"{__container_worker_count(worker_count_file) + 1}")
        if not service_file.is_file():
            log.info(f"Service file not found. Starting compose services for {service_file_name}...", worker_id=worker_id)
            compose_instance = DockerCompose(
                context=context,
                compose_file_name=compose_file_name,
                wait=True,
            )
            compose_instance.start()
            service_details = service_details_supplier(compose_instance)
            __write_service_file(tmp_path_factory, service_file.name, service_details)
            log.info(f"Compose services for {service_file_name} started and service file written.", worker_id=worker_id)

    # All workers will yield the service details from the file
    yield json.loads(service_file.read_text())

    # Teardown logic
    log.info(f"Tearing down docker compose {service_file_name} fixture...", worker_id=worker_id)
    with FileLock(str(lock_file)):
        worker_count_file.write_text(f"{__container_worker_count(worker_count_file) - 1}")
        count = __container_worker_count(worker_count_file)
        if count == 0:
            log.info(f"Stopping compose services for {service_file_name}...", worker_id=worker_id)
            # Re-instantiate DockerCompose to stop the services
            compose = DockerCompose(context, compose_file_name=compose_file_name)
            compose.stop()
            log.info(f"Stopped compose services for {service_file_name}.", worker_id=worker_id)
            # Clean up control files
            service_file.unlink(missing_ok=True)
            worker_count_file.unlink(missing_ok=True)
            log.info(f"Service files for {service_file_name} removed.", worker_id=worker_id)


@pytest.fixture(scope="session")
def docker_compose_services(tmp_path_factory, worker_id) -> Generator[dict[str, Any], None, None]:
    """
    A session-scoped fixture that starts, manages, and stops the Outline
    Docker Compose environment for the entire test session using the
    __start_docker_compose helper.
    """

    def service_details_supplier(compose_instance: DockerCompose) -> dict[str, Any]:
        host = "localhost"
        port = compose_instance.get_service_port("outline", 3000)
        base_url = f"http://{host}:{port}"

        team_id, user_id = str(uuid.uuid4()), str(uuid.uuid4())
        api_key_secret = f"ol_api_{uuid.uuid4().hex}{uuid.uuid4().hex[:6]}"
        hashed_secret = hashlib.sha256(api_key_secret.encode()).hexdigest()

        default_postgres_port = 5432
        pg_host = compose_instance.get_service_host("postgres", default_postgres_port)
        pg_port = compose_instance.get_service_port("postgres", default_postgres_port)
        db_url = f"postgresql://outline:password@{pg_host}:{pg_port}/outline"

        # Database seeding commands
        commands = [
            __outline_team_sql(team_id),
            __outline_user_sql(user_id, team_id),
            __outline_api_key_sql(api_key_secret, hashed_secret, user_id),
        ]
        for cmd in commands:
            subprocess.run(["psql", db_url, "-c", cmd], check=True, capture_output=True)

        log.info("Finished seeding database. Waiting for Outline to process new data...")
        time.sleep(5)

        return {
            "outline_base_url": base_url,
            "api_key": api_key_secret,
            "db_url": db_url,
            "team_id": team_id,
            "user_id": user_id,
        }

    compose_directory_path = Path(__file__).parent / "docker" / "outline_test_env"
    yield from __start_docker_compose(
        tmp_path_factory,
        "outline_service",
        compose_directory_path,  # Passed as Path object, which is compatible with PathLike[str]
        "docker-compose.yml",
        service_details_supplier,
        worker_id,
    )


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


@pytest.fixture(scope="session")
def qdrant_service(tmp_path_factory, worker_id):
    """
    Fixture that starts a Qdrant container for the test session using the docker helper.
    """

    def container_supplier():
        return QdrantContainer("qdrant/qdrant:v1.16.0")

    def service_file_writer(qdrant_container: QdrantContainer):
        return {
            "host": qdrant_container.get_container_host_ip(),
            "http_port": qdrant_container.exposed_rest_port,
            "grpc_port": qdrant_container.exposed_grpc_port,
        }

    yield from __start_docker_container(tmp_path_factory, "qdrant_service", container_supplier, service_file_writer, worker_id)


def __start_docker_container(
    tmp_path_factory: pytest.TempPathFactory, service_file_name: str, container_supplier: Callable[[], DockerContainer], service_file_writer: Callable[[Any], dict[str, Any]], worker_id: str
) -> Generator[dict[str, Any], None, None]:
    log.info(f"Setting up docker {service_file_name} fixture...", worker_id=worker_id)
    service_file = __temp_file(tmp_path_factory, f"{service_file_name}.json")
    lock_file = __temp_file(tmp_path_factory, f"{service_file_name}.lock")
    worker_count = __temp_file(tmp_path_factory, f"{service_file_name}.count")
    container_id = __temp_file(tmp_path_factory, f"{service_file_name}.id")

    with FileLock(lock_file):
        worker_count.write_text(f"{__container_worker_count(worker_count) + 1}")
        if not service_file.is_file():
            log.info(f"Service file not found. Starting container for {service_file_name}...", worker_id=worker_id)
            container_instance = container_supplier()
            container_instance.start()
            service_details = service_file_writer(container_instance)
            __write_service_file(tmp_path_factory, service_file.name, service_details)
            container_id.write_text(container_instance.get_wrapped_container().id)
            log.info(f"Container for {service_file_name} started and service file written.", worker_id=worker_id)

    # All workers will yield the service details from the file
    yield json.loads(service_file.read_text())

    # Teardown logic
    log.info(f"Tearing down docker {service_file_name} fixture...", worker_id=worker_id)
    with FileLock(lock_file):
        worker_count.write_text(f"{__container_worker_count(worker_count) - 1}")
        count = __container_worker_count(worker_count)
        if count == 0:
            __stop_container(container_id.read_text(), service_file_name, worker_id)
            service_file.unlink(missing_ok=True)
            container_id.unlink(missing_ok=True)
            worker_count.unlink(missing_ok=True)
            log.info(f"Container for {service_file_name} stopped and service file removed.", worker_id=worker_id)


def __container_worker_count(file: Path) -> int:
    if not file.is_file():
        return 0
    content = file.read_text()
    return int(content) if content else 0


def __stop_container(container_id: str, service_file_name: str, worker_id: str):
    try:
        log.info(f"Stopping container for {service_file_name}...", worker_id=worker_id)
        container = docker.from_env().containers.get(container_id)
        container.stop()
        container.remove()
    except Exception as e:
        log.warning(f"Container {container_id} could not be stopped: {e}")


@pytest.fixture
def qdrant_tool(qdrant_service: dict[str, Any]):
    """
    Fixture that provides an instance of the QdrantTool, configured to
    connect to the Qdrant service running in the test container.
    """
    return QdrantTool(
        host=qdrant_service["host"],
        http_port=qdrant_service["http_port"],
        grpc_port=qdrant_service["grpc_port"],
    )
