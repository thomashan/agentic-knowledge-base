import pytest
from testcontainers.core.container import DockerContainer as GenericContainer


@pytest.mark.integration
def test_generic_container_starts():
    """
    Tests that a generic container can be started using testcontainers.
    """
    with GenericContainer("nginx:latest") as nginx:
        assert nginx.get_container_host_ip() is not None
