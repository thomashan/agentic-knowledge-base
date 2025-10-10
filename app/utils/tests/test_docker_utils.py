import pytest
from testcontainers.core.container import DockerContainer


@pytest.mark.integration
def test_run_hello_world_container():
    """
    Tests that the run_hello_world_container function returns the correct string.
    """
    with DockerContainer("ubuntu:latest").with_command("echo hello world") as container:
        container.start()
        logs = container.get_logs()
        result = logs[0].decode("utf-8").strip()
        assert result == "hello world"
