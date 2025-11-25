import typer
from agents_core.core import AbstractAgent, AbstractTask
from agents_intelligence.intelligence import IntelligenceAgent
from agents_knowledge.knowledge import KnowledgeAgent
from agents_planner.planner import PlannerAgent
from agents_retrieval.retrieval import RetrievalAgent
from crewai_adapter.adapter import CrewAIOrchestrator
from documentation.outline_tool import OutlineTool
from integration_llm.factory import LlmFactory
from runner.runner import Runner
from typer.cli import app
from vectordb.qdrant_tool import QdrantTool


class BasicTask(AbstractTask):
    def __init__(self, agent: AbstractAgent):
        self._agent = agent

    @property
    def description(self) -> str:
        return "Say hello and confirm you are working. Respond with just the word 'OK'."

    @property
    def expected_output(self) -> str:
        return "The word 'OK'"

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list[AbstractTask] | None:
        return None


@app.command()
def main(
    query: str = typer.Argument(..., help="The user query to be processed."),
    provider: str = typer.Option("ollama", help="The LLM provider to use (e.g., 'ollama', 'openai')."),
    model: str = typer.Option("gemma2:2b", help="The specific model name to use."),
    base_url: str | None = typer.Option(None, help="The base URL for the LLM server (for providers like ollama)."),
    api_key: str | None = typer.Option(None, help="The API key for the LLM provider (for providers like openai)."),
    workflow: str = typer.Option("planner", help="The type of workflow to execute (e.g., 'planner', 'full-rag')."),
):
    """
    Initializes and runs the agentic workflow based on the provided query and LLM configuration.
    """
    agents = []
    tasks = []

    # 1. Build LLM config and create LLM via factory
    llm_config = {
        "provider": provider,
        "model": model,
        "base_url": base_url,
        "api_key": api_key,
    }
    # Filter out None values so we don't pass them to the factory
    llm_config = {k: v for k, v in llm_config.items() if v is not None}

    llm = LlmFactory.create_llm(llm_config)

    # 2. Configure agents and tasks based on the workflow type
    if workflow == "planner":
        planner = PlannerAgent(llm=llm)
        agents.append(planner)
        plan_task = BasicTask(description=f"Create a step-by-step plan to answer the user's query: '{query}'", expected_output="A list of tasks in a structured format.", agent=planner)
        tasks.append(plan_task)
    elif workflow == "full-rag":
        # Instantiate Tools (using MagicMock for unimplemented tools)
        qdrant_tool = QdrantTool()  # Assume default config for now
        outline_tool = OutlineTool()  # Assume default config for now

        # Instantiate Agents
        planner = PlannerAgent(llm=llm)
        intelligence_agent = IntelligenceAgent(llm=llm)
        knowledge_agent = KnowledgeAgent(llm=llm, qdrant_tool=qdrant_tool, outline_tool=outline_tool)
        retrieval_agent = RetrievalAgent(llm=llm, qdrant_tool=qdrant_tool)

        agents.extend([planner, intelligence_agent, knowledge_agent, retrieval_agent])

        # Instantiate Tasks (simplified, sequential flow for now)
        plan_task = BasicTask(description=f"Create a detailed plan for full RAG workflow for query: '{query}'", expected_output="A structured list of analysis, and persistence steps.", agent=planner)
        intelligence_task = BasicTask(
            description=f"Analyze and synthesize information into an intelligence report for query: '{query}'", expected_output="A structured intelligence report.", agent=intelligence_agent
        )
        knowledge_persistence_task = BasicTask(
            description=f"Persist the intelligence report into the knowledge base for query: '{query}'",
            expected_output="Confirmation of successful knowledge persistence (document URL, vector IDs).",
            agent=knowledge_agent,
        )
        retrieval_and_answer_task = BasicTask(
            description=f"Retrieve relevant information and provide a final answer for query: '{query}'",
            expected_output="A concise and accurate final answer based on retrieved knowledge.",
            agent=retrieval_agent,
        )

        tasks.extend([plan_task, intelligence_task, knowledge_persistence_task, retrieval_and_answer_task])

    else:
        typer.echo(f"Error: Unknown workflow: {workflow}", err=True)
        raise typer.Exit(code=1)

    # 3. Instantiate the Orchestrator and configure it
    orchestrator = CrewAIOrchestrator(config=None)  # Assume default config for now
    for agent in agents:
        orchestrator.add_agent(agent)
    for task in tasks:
        orchestrator.add_task(task)

    # 4. Instantiate the Runner with the pre-configured orchestrator
    runner = Runner(orchestrator=orchestrator)

    # 5. Run the workflow
    runner.run(query)


if __name__ == "__main__":
    app()
