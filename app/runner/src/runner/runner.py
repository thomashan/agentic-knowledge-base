from typing import Any

from agents_core.core import AbstractAgent, AbstractLLM, AbstractOrchestrator, AbstractTask, AbstractTool
from agents_intelligence.intelligence import IntelligenceAgent
from agents_knowledge.knowledge import KnowledgeAgent
from agents_orchestrator.factory.factory import OrchestratorFactory

# Agent Models
from agents_planner.models import Plan  # PlannerTask is the Pydantic model
from agents_planner.models import Task as PlannerTask

# Agent Implementations
from agents_planner.planner import PlannerAgent
from agents_research.research import ResearchAgent
from crewai.llm import LLM  # crewai's LLM type, often used by Agents

# Tool Implementations
from documentation_outline.outline_tool import OutlineTool  # From integration-documentation
from integration_llm.factory import create_llm
from pydantic import BaseModel, Field

# SentenceTransformer for embedding_model
from sentence_transformers import SentenceTransformer
from vectordb_qdrant.qdrant_tool import QdrantTool  # From integration-vectordb-qdrant

# Centralized Settings
from .config import Settings


# --- Placeholder Tools ---
class DemoSearchArgs(BaseModel):
    query: str = Field(..., description="The query to search for.")


class DemoSearchTool(AbstractTool):
    @property
    def name(self) -> str:
        return "Demo Search Tool"

    @property
    def description(self) -> str:
        return "A placeholder search tool."

    @property
    def args_schema(self) -> type[BaseModel]:
        return DemoSearchArgs

    def execute(self, **kwargs: Any) -> str:
        query = kwargs.get("query", "no query provided")
        return f"Demo Search Result for '{query}'"

    def get_command_schemas(self) -> dict[str, type[BaseModel]] | None:
        return None


class DemoScrapeArgs(BaseModel):
    url: str = Field(..., description="The URL to scrape.")


class DemoScrapeTool(AbstractTool):
    @property
    def name(self) -> str:
        return "Demo Scrape Tool"

    @property
    def description(self) -> str:
        return "A placeholder scrape tool."

    @property
    def args_schema(self) -> type[BaseModel]:
        return DemoScrapeArgs

    def execute(self, **kwargs: Any) -> str:
        url = kwargs.get("url", "no url provided")
        return f"Demo Scraped Content from '{url}'"

    def get_command_schemas(self) -> dict[str, type[BaseModel]] | None:
        return None


# --- Wrapper for PlannerTask to AbstractTask ---
class OrchestratorTask(AbstractTask):
    """A wrapper for PlannerTask.Task to conform to AbstractTask interface."""

    def __init__(self, planner_task: PlannerTask, agent_instance: AbstractAgent, dependencies: list[AbstractTask] | None = None):
        self._planner_task = planner_task
        self._agent = agent_instance  # Store the AbstractAgent instance
        self._dependencies = dependencies or []

    @property
    def description(self) -> str:
        return self._planner_task.description

    @property
    def expected_output(self) -> str:
        return self._planner_task.expected_output

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list[AbstractTask] | None:
        # Proper dependency resolution would require mapping task_ids to AbstractTask instances.
        # For simplicity in this initial CLI runner, we'll assume independent tasks or simple chaining.
        return self._dependencies


class Runner:
    def __init__(
        self,
        settings: Settings,
        orchestrator_config: dict[str, Any] | None = None,
    ):
        """
        Initializes the Runner by setting up the LLM, orchestrator, and core agents
        using a centralized Settings object.

        Args:
            settings: The application settings object.
            orchestrator_config: Optional configuration for the orchestrator.
        """
        self.settings = settings
        self.orchestrator_config = orchestrator_config or {}

        # 1. Create LLM from settings
        self.abstract_llm: AbstractLLM = create_llm(
            model=self.settings.llm_model,
            provider=self.settings.llm_provider,
            base_url=self.settings.llm_base_url,
            orchestrator_type=self.settings.orchestrator_type,
        )
        self.crewai_llm: LLM = self.abstract_llm.llm()  # Get the crewai.LLM instance

        # 2. Create Orchestrator
        orchestrator_factory = OrchestratorFactory()
        self.orchestrator: AbstractOrchestrator = orchestrator_factory.create(self.settings.orchestrator_type, self.orchestrator_config)

        # 3. Instantiate Tools from settings
        self.documentation_tool = OutlineTool(api_key=self.settings.outline_api_key, base_url=self.settings.outline_base_url, collection_id=self.settings.outline_collection_id)

        self.vectordb_tool = QdrantTool(host=self.settings.qdrant_host, grpc_port=self.settings.qdrant_grpc_port, http_port=self.settings.qdrant_http_port)

        # Embedding Model (SentenceTransformer)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Placeholder Search and Scrape Tools
        self.search_tool = DemoSearchTool()
        self.scrape_tool = DemoScrapeTool()

        # 4. Instantiate and add Core Agents
        self.agent_instances: dict[str, AbstractAgent] = {}

        self.planner_agent = PlannerAgent(llm=self.abstract_llm)  # Planner takes AbstractLLM
        self.agent_instances[self.planner_agent.role] = self.planner_agent
        self.orchestrator.add_agent(self.planner_agent)

        self.research_agent = ResearchAgent(llm=self.abstract_llm, search_tool=self.search_tool, scrape_tool=self.scrape_tool)
        self.agent_instances[self.research_agent.role] = self.research_agent
        self.orchestrator.add_agent(self.research_agent)

        self.knowledge_agent = KnowledgeAgent(
            documentation_tool=self.documentation_tool,
            vectordb_tool=self.vectordb_tool,
            embedding_model=self.embedding_model,
            llm=self.abstract_llm,
        )
        self.agent_instances[self.knowledge_agent.role] = self.knowledge_agent
        self.orchestrator.add_agent(self.knowledge_agent)

        self.intelligence_agent = IntelligenceAgent(llm=self.abstract_llm)
        self.agent_instances[self.intelligence_agent.role] = self.intelligence_agent
        self.orchestrator.add_agent(self.intelligence_agent)

    def run(self, query: str) -> str:
        """
        Executes the main orchestration logic, with agents dynamically generating tasks.
        """
        try:
            # PlannerAgent generates a Plan
            plan: Plan = self.planner_agent.generate_plan(query)

            # Convert PlannerTasks to OrchestratorTasks and add to orchestrator
            for planner_task in plan.tasks:
                # Find the correct AbstractAgent instance based on the role string
                agent_for_task = self.agent_instances.get(planner_task.agent)
                if not agent_for_task:
                    # If the planner assigns a task to an unknown agent, it's an error
                    raise ValueError(f"Agent with role '{planner_task.agent}' not found for task '{planner_task.description}'")

                # Note: This simple mapping of dependencies is for basic sequential processing.
                # More complex plans would require mapping task_ids to AbstractTask objects.
                orchestrator_task = OrchestratorTask(planner_task=planner_task, agent_instance=agent_for_task)
                self.orchestrator.add_task(orchestrator_task)

            execution_result = self.orchestrator.execute()
            return execution_result.raw_output
        except Exception as e:
            import traceback

            traceback.print_exc()  # Print full traceback for debugging
            return f"Error during workflow execution: {type(e).__name__}: {e}"
