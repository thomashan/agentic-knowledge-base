from typing import Any

from agents_core.core import (
    AbstractAgent,
    AbstractOrchestrator,
    AbstractTask,
    AbstractTool,
    ExecutionResult,
    TaskExecutionRecord,
)


# Concrete implementations for testing abstract classes
class ConcreteTool(AbstractTool):
    """A concrete implementation of AbstractTool for testing purposes."""

    @property
    def name(self) -> str:
        return "concrete_tool"

    @property
    def description(self) -> str:
        return "A concrete tool for testing."

    def execute(self, **kwargs: Any) -> Any:
        return f"executed with {kwargs}"


class ConcreteAgent(AbstractAgent):
    """A concrete implementation of AbstractAgent for testing purposes."""

    def __init__(self, tools: list[AbstractTool] = None):
        self._tools = tools or []

    @property
    def role(self) -> str:
        return "Test Agent"

    @property
    def goal(self) -> str:
        return "To test abstract agents."

    @property
    def backstory(self) -> str:
        return "I am a test agent."

    @property
    def tools(self) -> list[AbstractTool]:
        return self._tools

    @property
    def llm_config(self) -> dict[str, Any]:
        return {"model": "test-model"}


class ConcreteTask(AbstractTask):
    """A concrete implementation of AbstractTask for testing purposes."""

    def __init__(
        self,
        agent: AbstractAgent,
        dependencies: list["AbstractTask"] = None,
    ):
        self._agent = agent
        self._dependencies = dependencies or []

    @property
    def description(self) -> str:
        return "A test task."

    @property
    def expected_output(self) -> str:
        return "A successful test execution."

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list["AbstractTask"]:
        return self._dependencies


class ConcreteOrchestrator(AbstractOrchestrator):
    """A concrete implementation of AbstractOrchestrator for testing purposes."""

    def __init__(self, config: dict[str, Any] = None):
        self.config = config if config is not None else {}
        self.agents: list[AbstractAgent] = []
        self.tasks: list[AbstractTask] = []

    def add_agent(self, agent: AbstractAgent) -> None:
        self.agents.append(agent)

    def add_task(self, task: AbstractTask) -> None:
        self.tasks.append(task)

    def execute(self) -> ExecutionResult:
        return ExecutionResult(
            raw_output="Orchestration executed successfully. Final result.",
            structured_output=None,
            task_outputs=[],
            metadata={},
        )


class TestAbstractInterfaces:
    """Test cases for the abstract interfaces and their concrete implementations."""

    def test_concrete_tool(self):
        """Tests the ConcreteTool implementation."""
        tool = ConcreteTool()
        assert tool.name == "concrete_tool"
        assert tool.description == "A concrete tool for testing."
        assert tool.execute(param="test") == "executed with {'param': 'test'}"

    def test_concrete_agent(self):
        """Tests the ConcreteAgent implementation."""
        tool1 = ConcreteTool()
        agent = ConcreteAgent(tools=[tool1])
        assert agent.role == "Test Agent"
        assert agent.goal == "To test abstract agents."
        assert agent.backstory == "I am a test agent."
        assert agent.tools == [tool1]
        assert agent.llm_config == {"model": "test-model"}

    def test_concrete_task(self):
        """Tests the ConcreteTask implementation."""
        agent = ConcreteAgent()
        task1 = ConcreteTask(agent=agent)
        task2 = ConcreteTask(agent=agent, dependencies=[task1])

        assert task1.description == "A test task."
        assert task1.expected_output == "A successful test execution."
        assert task1.agent is agent
        assert task1.dependencies == []
        assert task2.dependencies == [task1]

    def test_concrete_orchestrator(self):
        """Tests the ConcreteOrchestrator implementation."""
        orchestrator = ConcreteOrchestrator(config={"key": "value"})
        agent = ConcreteAgent()
        task = ConcreteTask(agent=agent)

        orchestrator.add_agent(agent)
        orchestrator.add_task(task)

        assert orchestrator.config == {"key": "value"}
        assert orchestrator.agents == [agent]
        assert orchestrator.tasks == [task]

        result = orchestrator.execute()
        assert result.raw_output == "Orchestration executed successfully. Final result."
        assert result.structured_output is None
        assert result.task_outputs == []
        assert result.metadata == {}

    def test_task_execution_record_instantiation(self):
        """Tests the instantiation of the TaskExecutionRecord model."""
        record = TaskExecutionRecord(
            task_description="Test task",
            raw_output="Test output",
            structured_output=None,
        )
        assert record.task_description == "Test task"
        assert record.raw_output == "Test output"
        assert record.structured_output is None

    def test_execution_result_instantiation(self):
        """Tests the instantiation of the ExecutionResult model."""
        result = ExecutionResult(
            raw_output="Final output",
            structured_output=None,
            task_outputs=[],
            metadata={},
        )
        assert result.raw_output == "Final output"
        assert result.structured_output is None
        assert result.task_outputs == []
        assert result.metadata == {}
