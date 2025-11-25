from agents_core.core import AbstractAgent, AbstractOrchestrator, AbstractTask


class Runner:
    def __init__(
        self,
        orchestrator_cls: type[AbstractOrchestrator],
        agents: list[AbstractAgent],
        tasks: list[AbstractTask],
        orchestrator_config: dict = None,
    ):
        """
        Initializes the Runner.

        Args:
            orchestrator_cls: The class of the orchestrator to use (e.g., CrewAIOrchestrator).
            agents: A list of agent objects that adhere to the AbstractAgent interface.
            tasks: A list of task objects that adhere to the AbstractTask interface.
            orchestrator_config: Optional configuration for the orchestrator.
        """
        self.orchestrator = orchestrator_cls(config=orchestrator_config)
        for agent in agents:
            self.orchestrator.add_agent(agent)
        for task in tasks:
            self.orchestrator.add_task(task)

    def run(self, query: str) -> str:
        """
        Executes the main orchestration logic.
        The query is currently unused as the context is expected to be in the tasks.
        """
        execution_result = self.orchestrator.execute()
        return execution_result.raw_output
