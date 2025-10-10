from typing import Any

from agents_core.core import AbstractAgent, AbstractOrchestrator, AbstractTask, AbstractTool, ExecutionResult
from crewai import Agent, Crew, Task
from crewai.tools import BaseTool


class CrewAITool(BaseTool):
    """A wrapper for AbstractTool to be used with CrewAI."""
    name: str
    description: str
    _abstract_tool: AbstractTool

    def __init__(self, abstract_tool: AbstractTool):
        super().__init__(name=abstract_tool.name, description=abstract_tool.description)
        self._abstract_tool = abstract_tool

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Executes the wrapped AbstractTool's execute method."""
        return self._abstract_tool.execute(*args, **kwargs)


class CrewAIOrchestrator(AbstractOrchestrator):
    """A CrewAI orchestrator adapter."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initializes the orchestrator with framework-specific configuration."""
        self.crewai_agents: list[Agent] = []
        self.crewai_tasks: list[Task] = []
        self.agent_map: dict[int, Agent] = {}
        self.config = config or {}

    def add_agent(self, agent: AbstractAgent) -> None:
        """Registers an abstract agent with the orchestrator."""
        crewai_tools = [
            CrewAITool(abstract_tool=tool)
            for tool in agent.tools or []
        ]
        llm = agent.llm_config.get("client") if agent.llm_config else None
        crewai_agent = Agent(
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            tools=crewai_tools,
            llm=llm,
        )
        self.crewai_agents.append(crewai_agent)
        self.agent_map[id(agent)] = crewai_agent

    def add_task(self, task: AbstractTask) -> None:
        """Registers an abstract task with the orchestrator."""
        crewai_agent = self.agent_map.get(id(task.agent))
        if not crewai_agent:
            raise ValueError(f"Agent for task '{task.description}' not found.")

        crewai_task = Task(
            description=task.description,
            expected_output=task.expected_output,
            agent=crewai_agent,
        )
        self.crewai_tasks.append(crewai_task)

    def execute(self) -> ExecutionResult:
        """
        Executes the defined orchestration process and returns a standardized result.
        """
        crew = Crew(agents=self.crewai_agents, tasks=self.crewai_tasks, **self.config)

        result = crew.kickoff()

        return ExecutionResult(raw_output=result)
