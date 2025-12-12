import json
from typing import Any

from agents_core.core import AbstractAgent, AbstractLLM, AbstractOrchestrator, AbstractTask, AbstractTool, ExecutionResult
from crewai import LLM, Agent, Crew, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CrewAILLM(AbstractLLM[LLM]):
    def __init__(self, crew_llm: LLM):
        self.crew_llm = crew_llm

    def call(self, prompt: str) -> str:
        return self.crew_llm.call(prompt)

    def llm(self) -> LLM:
        return self.crew_llm


class SearchToolArgs(BaseModel):
    query: str = Field(..., description="The query to search for.")


class ScrapeToolArgs(BaseModel):
    url: str = Field(..., description="The URL to scrape.")


class QdrantToolArgs(BaseModel):
    command: str = Field(..., description="The command to execute on Qdrant (e.g., 'upsert_vectors', 'search_vectors', 'delete_vectors').")

    class Config:
        extra = "allow"


class DocumentationToolArgs(BaseModel):
    command: str = Field(..., description="The command to execute on the documentation tool (e.g., 'create_or_update_document', 'publish_document', 'get_document', 'delete_document').")

    class Config:
        extra = "allow"


class DynamicArgsSchema(BaseModel):
    """A generic schema to capture any arguments for dynamic tools."""

    class Config:
        extra = "allow"  # Allow extra fields


class PydanticAbstractToolWrapper(BaseModel):
    tool_instance: AbstractTool = Field(..., exclude=True)

    class Config:
        arbitrary_types_allowed = True


class CrewAITool(BaseTool):
    """A wrapper to make an AbstractTool compatible with CrewAI."""

    args_schema: type[BaseModel] = DynamicArgsSchema  # Explicitly define args_schema at class level
    wrapped_tool_field: PydanticAbstractToolWrapper = Field(..., exclude=True)

    def __init__(self, tool: AbstractTool, args_schema: BaseModel | None = None, **kwargs):
        tool_wrapper = PydanticAbstractToolWrapper(tool_instance=tool)
        super().__init__(name=tool.name, description=tool.description, wrapped_tool_field=tool_wrapper, **kwargs)

        if args_schema:
            self.args_schema = args_schema
        # Dynamically set args_schema based on the tool's name
        elif tool.name == "Demo Search Tool":
            self.args_schema = SearchToolArgs
        elif tool.name == "Demo Scrape Tool":
            self.args_schema = ScrapeToolArgs
        elif tool.name == "Qdrant VectorDB Tool":
            self.args_schema = QdrantToolArgs
        elif tool.name == "Documentation Tool":
            self.args_schema = DocumentationToolArgs
        else:
            # Fallback for other tools, allowing any extra fields
            self.args_schema = DynamicArgsSchema

    def _run(self, **kwargs: Any) -> str:
        # CrewAI sometimes wraps arguments under a 'kwargs' key, or passes a single 'input' key.
        # We need to unwrap these if present to get the actual arguments for the tool.
        final_kwargs = kwargs
        if len(kwargs) == 1 and "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
            final_kwargs = kwargs["kwargs"]
        elif len(kwargs) == 1 and "input" in kwargs and isinstance(kwargs["input"], str):
            # If CrewAI passes arguments under a generic 'input' key, try to parse it as JSON.
            # If not JSON, assume the 'input' string itself might contain the value.
            try:
                parsed_input = json.loads(kwargs["input"])
                if isinstance(parsed_input, dict):
                    final_kwargs = parsed_input
                else:  # if input is just a string, try to infer meaning
                    final_kwargs = {"__default_arg__": kwargs["input"]}  # Placeholder
            except json.JSONDecodeError:
                final_kwargs = {"__default_arg__": kwargs["input"]}  # Fallback if not valid JSON

        # Generalized Fallback: If required arguments are still missing, try to extract from 'description'
        # This is a heuristic to handle LLMs that output generic descriptions instead of structured args.
        if "description" in final_kwargs and isinstance(final_kwargs["description"], str):
            description_text = final_kwargs["description"]

            # Attempt to extract 'query'
            if "query" not in final_kwargs and "search" in self.name.lower():
                # Simple heuristic: if 'query' is missing and tool is a search tool, use description
                final_kwargs["query"] = description_text

            # Attempt to extract 'url'
            if "url" not in final_kwargs and "scrape" in self.name.lower():
                # Simple heuristic: if 'url' is missing and tool is a scrape tool, use description
                # More robust: try to find an actual URL in the description
                import re

                url_match = re.search(r'https?://[^\s<>"]+|www\.[^\s<>"]+', description_text)
                if url_match:
                    final_kwargs["url"] = url_match.group(0)
                else:
                    final_kwargs["url"] = description_text  # Fallback to full description

            # Attempt to extract 'command' for Qdrant/Documentation
            if "command" not in final_kwargs and ("vectordb" in self.name.lower() or "documentation" in self.name.lower()):
                # This is more complex, as 'command' needs to be one of predefined values.
                # For now, let's look for keywords. This is very weak and needs refinement.
                if "upsert" in description_text.lower():
                    final_kwargs["command"] = "upsert_vectors"
                elif "search" in description_text.lower():
                    final_kwargs["command"] = "search_vectors"
                elif "delete" in description_text.lower():
                    final_kwargs["command"] = "delete_vectors"
                elif "create" in description_text.lower() or "update" in description_text.lower() or "publish" in description_text.lower():
                    final_kwargs["command"] = "create_or_update_document"
                elif "get" in description_text.lower():
                    final_kwargs["command"] = "get_document"
                # If command is still not found, we might try to extract 'title'/'content' from description
                # This is getting very complex for a generic heuristic.
                # For now, if 'command' is not found by keywords, let it fail for Qdrant/Documentation.

        # Clean up generic description/input fields that might interfere with tool validation
        final_kwargs.pop("description", None)
        final_kwargs.pop("type", None)  # Often accompanied with description from LLM
        final_kwargs.pop("__default_arg__", None)  # Remove our placeholder
        final_kwargs.pop("security_context", None)  # Remove CrewAI's internal security_context

        return self.wrapped_tool_field.tool_instance.execute(**final_kwargs)


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
