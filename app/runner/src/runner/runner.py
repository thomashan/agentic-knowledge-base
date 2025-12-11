from agents_core.core import AbstractOrchestrator


class Runner:
    def __init__(
        self,
        orchestrator: AbstractOrchestrator,
    ):
        """
        Initializes the Runner with a pre-configured orchestrator.
        Args:
            orchestrator: An instance of a class that implements AbstractOrchestrator.
        """
        self.orchestrator = orchestrator

    def run(self, query: str) -> str:
        """
        Executes the main orchestration logic.
        The query is currently unused as the context is expected to be in the tasks.
        """
        execution_result = self.orchestrator.execute()
        return execution_result.raw_output
