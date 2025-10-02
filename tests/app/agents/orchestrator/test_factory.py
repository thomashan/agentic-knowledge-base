from app.agents.orchestrator.factory import OrchestratorFactory
from app.agents.orchestrator.crewai.adapter import CrewAIOrchestrator

def test_orchestrator_factory_create_crewai():
    """Tests the creation of a CrewAIOrchestrator using the factory."""
    factory = OrchestratorFactory()
    orchestrator = factory.create("crewai")
    assert isinstance(orchestrator, CrewAIOrchestrator)
