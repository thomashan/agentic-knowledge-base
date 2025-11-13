import pytest
import structlog
from agents_core.core import AbstractAgent, AbstractLLM, AbstractTask, AbstractTool
from crewai_adapter.adapter import CrewAILLM, CrewAIOrchestrator

log = structlog.get_logger()


class SimpleAgent(AbstractAgent):
    def __init__(self, llm: AbstractLLM):
        self._llm = llm

    @property
    def llm(self) -> AbstractLLM:
        return self._llm

    @property
    def role(self) -> str:
        return "Simple Agent"

    @property
    def goal(self) -> str:
        return "To be simple and respond to a simple task."

    @property
    def backstory(self) -> str:
        return "I am a simple agent created for a test."

    @property
    def prompt_template(self) -> None:
        return None

    @property
    def tools(self) -> list[AbstractTool]:
        return []

    @property
    def llm_config(self) -> None:
        return None

    @property
    def max_retries(self) -> int:
        return 1


class SimpleTask(AbstractTask):
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


@pytest.mark.integration
def test_simple_agent_flow(llm_factory):
    """
    Tests a simple end-to-end agent flow using the CrewAIOrchestrator
    with a real LLM client.
    """
    crew_llm = llm_factory("gemma2:2b")
    llm_adapter = CrewAILLM(crew_llm)
    orchestrator = CrewAIOrchestrator()

    agent = SimpleAgent(llm=llm_adapter)
    task = SimpleTask(agent=agent)

    orchestrator.add_agent(agent)
    orchestrator.add_task(task)

    try:
        result = orchestrator.execute()
        log.info(f"Agent flow execution result: {result.raw_output}")

        assert result is not None
        assert isinstance(result.raw_output, str)
        assert len(result.raw_output.strip()) > 0
        assert "ok" in result.raw_output.lower()

    except Exception as e:
        pytest.fail(f"Agent flow execution failed with an unexpected error: {e}")


if __name__ == "__main__":
    pytest.main()
