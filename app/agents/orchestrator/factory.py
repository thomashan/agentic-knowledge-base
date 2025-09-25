# app/agents/orchestrator/factory.py

from typing import Dict, Type, Any
from app.agents.core.abc import AbstractOrchestrator
from app.agents.orchestrator.crewai.adapter import CrewAIOrchestrator

class OrchestratorFactory:
    def __init__(self):
        self._orchestrators: Dict[str, Type[AbstractOrchestrator]] = {
            "crewai": CrewAIOrchestrator,
        }

    def create(self, orchestrator_type: str, config: Dict[str, Any] = None) -> AbstractOrchestrator:
        orchestrator_class = self._orchestrators.get(orchestrator_type)
        if not orchestrator_class:
            raise ValueError(f"Unknown orchestrator type: {orchestrator_type}")
        return orchestrator_class(config=config)
