from typing import Any

from agents_core.core import AbstractAgent, AbstractLLM, AbstractOrchestrator, AbstractTask, AbstractTool, ExecutionResult
from crewai import LLM, Agent, Crew, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, PrivateAttr


class CrewAILLM(AbstractLLM[LLM]):
    def __init__(self, crew_llm: LLM):
        self.crew_llm = crew_llm

    def call(self, prompt: str) -> str:
        return self.crew_llm.call(prompt)

    def llm(self) -> LLM:
        return self.crew_llm


class NoArgs(BaseModel):
    """No arguments needed for this tool."""

    pass


class CrewAITool(BaseTool):
    """
    A unified wrapper to make an AbstractTool compatible with CrewAI.
    Can wrap an entire tool (if no command_name is provided) or a specific command of a tool.
    """

    _tool: AbstractTool = PrivateAttr()
    _command_name: str | None = PrivateAttr(default=None)

    def __init__(self, tool: AbstractTool, command_name: str | None = None, args_schema: type[BaseModel] | None = None, **kwargs):
        # Determine the schema
        if args_schema is None:
            args_schema = getattr(tool, "args_schema", None)
            if args_schema is None:
                args_schema = NoArgs

        # Determine name and description
        tool_name = tool.name
        tool_description = tool.description
        if command_name:
            tool_name = f"{tool.name.replace(' ', '_')}_{command_name}"
            tool_description = f"Executes the '{command_name}' command on the {tool.name}."

        # BaseTool (Pydantic model) initialization
        # We pass name/description via kwargs to super().__init__ if not overridden here,
        # but BaseTool usually takes them as fields.
        # Since we are overriding __init__, we must call super with the correct fields.

        # Note: BaseTool uses Pydantic fields for name/description/args_schema.
        super().__init__(name=tool_name, description=tool_description, args_schema=args_schema, **kwargs)

        self._tool = tool
        self._command_name = command_name

    def _run(self, **kwargs: Any) -> str:
        # 1. Handle nested arguments (CrewAI quirk)
        if len(kwargs) == 1:
            if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
                kwargs = kwargs["kwargs"]
            elif "arguments" in kwargs and isinstance(kwargs["arguments"], dict):
                kwargs = kwargs["arguments"]

        # 2. Sanitize "None" strings (LLM quirk)
        kwargs = {k: v for k, v in kwargs.items() if v != "None"}

        # 3. Strict Schema Filtering (Prevent Hallucinations)
        # Filter kwargs to only include arguments defined in the schema
        if self.args_schema and self.args_schema is not NoArgs:
            kwargs = {k: v for k, v in kwargs.items() if k in self.args_schema.model_fields}

        # 4. Execute
        if self._command_name:
            return self._tool.execute(command=self._command_name, **kwargs)
        else:
            return self._tool.execute(**kwargs)


def _create_crewai_tools_from_abstract_tool(tool: AbstractTool) -> list[BaseTool]:
    """
    Creates a list of crewAI-compatible tools from a single AbstractTool.
    If the AbstractTool has multiple commands, it creates a specialized tool for each.
    Otherwise, it creates a single generic tool.
    """
    command_schemas = tool.get_command_schemas()
    if not command_schemas:
        # Fallback to a single generic tool
        return [CrewAITool(tool)]

    tools = []
    for command_name, schema in command_schemas.items():
        command_tool_instance = CrewAITool(tool=tool, command_name=command_name, args_schema=schema)
        tools.append(command_tool_instance)
    return tools


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
        crewai_tools = []
        if agent.tools:
            for tool in agent.tools:
                crewai_tools.extend(_create_crewai_tools_from_abstract_tool(tool))

        llm_to_use = agent.llm
        if isinstance(llm_to_use, CrewAILLM):
            llm_to_use = llm_to_use.crew_llm

        crewai_agent = Agent(
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            tools=crewai_tools,
            llm=llm_to_use,
            allow_delegation=False,
            verbose=self.config.get("verbose", False),
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
        crew = Crew(name="Agentic Knowledge Base Crew", agents=self.crewai_agents, tasks=self.crewai_tasks, **self.config)

        result = crew.kickoff()

        raw_output = result.raw if hasattr(result, "raw") else result
        return ExecutionResult(raw_output=raw_output, structured_output=None)
