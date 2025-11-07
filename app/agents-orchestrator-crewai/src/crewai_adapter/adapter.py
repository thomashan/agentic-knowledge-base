from typing import Any

from agents_core.core import AbstractAgent, AbstractLLM, AbstractOrchestrator, AbstractTask, AbstractTool, ExecutionResult
from crewai import Agent, Crew, Task
from crewai.tools import BaseTool
from pydantic import BaseModel


class CrewAILLM(AbstractLLM):
    def __init__(self, crew_llm):
        self.crew_llm = crew_llm

    def call(self, prompt: str) -> str:
        return self.crew_llm.call(prompt)


class NoArgs(BaseModel):
    """No arguments needed for this tool."""

    pass


class CrewAITool(BaseTool):
    """A wrapper to make an AbstractTool compatible with CrewAI."""

    args_schema: type[BaseModel] = NoArgs

    def __init__(self, tool: AbstractTool):
        super().__init__(name=tool.name, description=tool.description)
        self._tool = tool

    def _run(self, **kwargs: Any) -> str:
        return self._tool.execute(**kwargs)


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
        crewai_tools = [CrewAITool(tool) for tool in agent.tools]

        # The new pattern is to pass the llm to the agent constructor.
        # The llm_config property of the agent should contain the llm instance.
        llm_to_use = agent.llm
        if isinstance(llm_to_use, CrewAILLM):
            llm_to_use = llm_to_use.crew_llm

        crewai_agent = Agent(
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            tools=crewai_tools,
            llm=llm_to_use,
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

        raw_output = result.raw if hasattr(result, "raw") else result
        return ExecutionResult(raw_output=raw_output)
