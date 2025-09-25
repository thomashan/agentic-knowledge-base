# app/agents/orchestrator/crewai/adapter.py

from typing import Any, Dict, Optional, List

from crewai import Agent, Task, Crew

from app.agents.core.abc import AbstractOrchestrator, AbstractAgent, AbstractTask
from app.agents.core.models import ExecutionResult


class CrewAIOrchestrator(AbstractOrchestrator):
    """A CrewAI orchestrator adapter."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initializes the orchestrator with framework-specific configuration."""
        self.crewai_agents: List[Agent] = []
        self.crewai_tasks: List[Task] = []
        self.agent_map: Dict[int, Agent] = {}
        self.config = config or {}

    def add_agent(self, agent: AbstractAgent) -> None:
        """Registers an abstract agent with the orchestrator."""
        crewai_agent = Agent(
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            tools=[tool for tool in agent.tools],
            llm=agent.llm_config,
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
        crew = Crew(
            agents=self.crewai_agents,
            tasks=self.crewai_tasks,
            **self.config
        )
        
        result = crew.kickoff()
        
        return ExecutionResult(raw_output=result)