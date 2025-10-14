import pytest
import structlog

log = structlog.get_logger()


@pytest.mark.integration
def test_place_holder():
    assert 1 == 1
