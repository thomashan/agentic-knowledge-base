from typing import Any

from agents_core.core import AbstractOrchestrator
from crewai_adapter.adapter import CrewAIOrchestrator


class OrchestratorFactory:
    def __init__(self):
        self._orchestrators: dict[str, type[AbstractOrchestrator]] = {
            "crewai": CrewAIOrchestrator,
        }

    def create(self, orchestrator_type: str, config: dict[str, Any] = None) -> AbstractOrchestrator:
        orchestrator_class = self._orchestrators.get(orchestrator_type)
        if not orchestrator_class:
            raise ValueError(f"Unknown orchestrator type: {orchestrator_type}")
        return orchestrator_class(config=config)
