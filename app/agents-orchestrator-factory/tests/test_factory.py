from unittest.mock import MagicMock

import pytest
from agents_core.core import AbstractOrchestrator
from crewai_adapter.adapter import CrewAIOrchestrator
from factory.factory import OrchestratorFactory


class MockOrchestrator(AbstractOrchestrator):
    def __init__(self, config: dict = None):
        self.config = config if config is not None else {}

    def add_agent(self, agent):  # type: ignore
        pass

    def add_task(self, task):  # type: ignore
        pass

    def execute(self):  # type: ignore
        pass


def test_orchestrator_factory_instantiation():
    """Tests the instantiation of the OrchestratorFactory."""
    factory = OrchestratorFactory()
    assert factory is not None


def test_orchestrator_factory_create_known_orchestrator(monkeypatch):
    """Tests creating a known orchestrator type."""
    mock_crewai_orchestrator_class = MagicMock(spec=CrewAIOrchestrator)
    mock_crewai_orchestrator_instance = MagicMock()
    mock_crewai_orchestrator_class.return_value = mock_crewai_orchestrator_instance

    monkeypatch.setattr("factory.factory.CrewAIOrchestrator", mock_crewai_orchestrator_class)

    factory = OrchestratorFactory()
    config = {"api_key": "test_key"}
    orchestrator = factory.create("crewai", config=config)

    mock_crewai_orchestrator_class.assert_called_once_with(config=config)
    assert orchestrator == mock_crewai_orchestrator_instance


def test_orchestrator_factory_create_unknown_orchestrator():
    """Tests creating an unknown orchestrator type raises a ValueError."""
    factory = OrchestratorFactory()
    with pytest.raises(ValueError, match="Unknown orchestrator type: unknown_type"):
        factory.create("unknown_type")

if __name__ == "__main__":
    pytest.main()
