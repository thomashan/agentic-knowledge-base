# CrewAI Orchestrator Documentation

This document provides guidance on configuring and using the `CrewAIOrchestrator` adapter within the agentic knowledge base system.

The `CrewAIOrchestrator` acts as an adapter, translating the framework-agnostic `AbstractAgent` and `AbstractTask` interfaces into CrewAI-specific agents and tasks, and then executing them using the CrewAI framework.

## Configuration

The `CrewAIOrchestrator` accepts a `config` dictionary during its instantiation. This dictionary is directly passed to the `crewai.Crew` constructor, allowing you to configure CrewAI-specific settings such as:

*   `process`: The process flow for the crew (e.g., `Process.sequential`, `Process.hierarchical`).
*   `manager_llm`: The LLM to be used by the crew manager in hierarchical processes.
*   `memory`: Whether to enable memory for the crew.
*   `verbose`: Verbosity level for CrewAI output.
*   Other `crewai.Crew` constructor parameters.

**Example Configuration:**

```python
config = {
    "process": "sequential",  # or "hierarchical"
    "verbose": True,
    "memory": False,
    # "manager_llm": ChatOpenAI(model="gpt-4"), # Example for hierarchical process
}
orchestrator = CrewAIOrchestrator(config=config)
```

## Usage

To use the `CrewAIOrchestrator`, you will interact with it using the `AbstractAgent` and `AbstractTask` interfaces defined in `agents_core.core`.

### 1. Define your Agents and Tasks

First, define your agents and tasks by implementing `AbstractAgent` and `AbstractTask`. Ensure your `AbstractAgent` instances are equipped with `AbstractTool` implementations if they need to use tools.

```python
from agents_core.core import AbstractAgent, AbstractTask, AbstractTool, ExecutionResult
from crewai_adapter.adapter import CrewAIOrchestrator
from typing import Any

# Example AbstractTool (assuming it's defined elsewhere or mocked)
class MyTool(AbstractTool):
    name: str = "search_tool"
    description: str = "A tool to search the internet."
    def execute(self, query: str) -> str:
        return f"Result for {query}"

class MyAgent(AbstractAgent):
    role: str = "Senior Researcher"
    goal: str = "Find relevant information on a topic"
    backstory: str = "An expert in information retrieval."
    tools: list[AbstractTool] = [MyTool()]
    llm_config: dict[str, Any] | None = {"model": "gpt-3.5-turbo"}

class MyTask(AbstractTask):
    description: str = "Research the latest AI trends."
    expected_output: str = "A summary of key AI trends."
    agent: AbstractAgent = MyAgent()
    dependencies: list[AbstractTask] | None = None

```

### 2. Instantiate and Configure the Orchestrator

```python
# Assuming MyAgent and MyTask are defined as above

orchestrator_config = {
    "process": "sequential",
    "verbose": True,
}
orchestrator = CrewAIOrchestrator(config=orchestrator_config)
```

### 3. Add Agents and Tasks

Add your `AbstractAgent` and `AbstractTask` instances to the orchestrator. The adapter will internally translate these into `crewai.Agent` and `crewai.Task` objects.

```python
# Assuming orchestrator, my_agent, and my_task are instantiated
orchestrator.add_agent(my_agent)
orchestrator.add_task(my_task)
```

### 4. Execute the Orchestration

Call the `execute` method to run the CrewAI workflow. The result will be returned as an `ExecutionResult` object.

```python
# Assuming agents and tasks have been added
result: ExecutionResult = orchestrator.execute()

print(f"Raw Output: {result.raw_output}")
# print(f"Structured Output: {result.structured_output}") # May be None
# print(f"Task Outputs: {result.task_outputs}") # May be empty
# print(f"Metadata: {result.metadata}") # May be empty
```

## Important Considerations

*   **LLM Configuration**: The `llm_config` property of `AbstractAgent` is passed directly to the `crewai.Agent` constructor. Ensure this dictionary is compatible with how CrewAI expects LLM configurations. For more advanced LLM handling, consider implementing a custom LLM factory or integrating with a centralized LLM management system.
*   **Tool Implementation**: `AbstractTool` instances are translated into `crewai.Tool` objects using their `name`, `description`, and `execute` method. Ensure your `AbstractTool` implementations are compatible with CrewAI's tool execution expectations.
*   **Output Parsing**: Currently, the `execute` method primarily captures the `raw_output` from `crew.kickoff()`. Populating `structured_output`, `task_outputs`, and `metadata` in `ExecutionResult` would require deeper integration with CrewAI's callback mechanisms to capture more granular execution details.
