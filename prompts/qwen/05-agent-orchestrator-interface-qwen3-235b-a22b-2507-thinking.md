### Implementation Plan for Orchestrator Abstraction

#### Goal

Create a framework-agnostic orchestrator interface that supports both CrewAI and LangChain implementations, with CrewAI as the initial implementation. Core abstractions will reside in `app/agents/core/`, while
framework-specific logic will be in `app/agents/orchestrator/{framework}/`.

---

### Step 1: Define Core Abstractions (`app/agents/core/`)

Create framework-agnostic ABCs that define the minimal contract for orchestrators, agents, and tasks.

#### File Structure

```
app/agents/core/
├── __init__.py
├── agent.py        # BaseAgent ABC
├── task.py         # BaseTask ABC
└── orchestrator.py # BaseOrchestrator ABC
```

#### Key Design Principles

1. **Minimal Viable Interface**: Only include properties/methods essential for *any* orchestrator
2. **No Framework Dependencies**: Core modules must import nothing from framework-specific code
3. **Explicit Contracts**: All implementations must satisfy these interfaces

---

### Core Interface Definitions

#### 1. `app/agents/core/agent.py`

```
"""Framework-agnostic agent interface.

This ABC defines the minimal contract for agents used in orchestrators.
Concrete implementations (CrewAI/LangChain) must satisfy this interface.
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    @property
    @abstractmethod
    def role(self) -> str:
        """The role/function of the agent (e.g., 'Researcher', 'Writer')."""
        pass

    @property
    @abstractmethod
    def goal(self) -> str:
        """The primary objective of the agent."""
        pass

    @property
    @abstractmethod
    def backstory(self) -> str:
        """Context/background information about the agent."""
        pass

    @property
    @abstractmethod
    def tools(self) -> list:
        """List of tools available to the agent (framework-agnostic representation)."""
        pass
```

#### 2. `app/agents/core/task.py`

```
"""Framework-agnostic task interface.

This ABC defines the minimal contract for tasks executed by orchestrators.
Concrete implementations must satisfy this interface.
"""

from abc import ABC, abstractmethod
from .agent import BaseAgent  # Only core dependency


class BaseTask(ABC):
    """Abstract base class for all tasks."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of what the task should accomplish."""
        pass

    @property
    @abstractmethod
    def expected_output(self) -> str:
        """Clear description of the expected output format/content."""
        pass

    @property
    @abstractmethod
    def agent(self) -> BaseAgent:
        """The agent responsible for executing this task."""
        pass

    @property
    @abstractmethod
    def context(self) -> list:
        """List of other tasks this task depends on (for dependency resolution)."""
        pass
```

#### 3. `app/agents/core/orchestrator.py`

```
"""Framework-agnostic orchestrator interface.

This ABC defines the contract for workflow orchestrators.
All orchestrator implementations (CrewAI/LangChain) must inherit from this.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from .agent import BaseAgent
from .task import BaseTask


class BaseOrchestrator(ABC):
    """Abstract base class for workflow orchestrators."""

    def __init__(self, agents: List[BaseAgent], tasks: List[BaseTask], **kwargs):
        """
        Initialize orchestrator with agents and tasks.
        
        Args:
            agents: List of agents implementing BaseAgent
            tasks: List of tasks implementing BaseTask
            kwargs: Framework-specific configuration options
            
        Note:
            Implementations should validate:
            - All task agents exist in the agents list
            - Task dependencies form a valid DAG
        """
        self.agents = agents
        self.tasks = tasks
        self._validate_configuration()

    @abstractmethod
    def kickoff(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the workflow and return results.
        
        Args:
            inputs: Optional dictionary of input parameters for the workflow
            
        Returns:
            Dictionary containing:
            - 'result': Final output of the workflow
            - 'intermediate_steps': Optional audit trail of execution
            
        Raises:
            OrchestratorError: For execution failures
        """
        pass

    @abstractmethod
    def _validate_configuration(self) -> None:
        """Validate agent/task configuration before execution."""
        pass


class OrchestratorError(Exception):
    """Base exception for orchestrator execution failures."""
    pass
```

---

### Step 2: CrewAI Implementation (`app/agents/orchestrator/crewai/`)

Implement the CrewAI-specific orchestrator that adheres to the core interfaces.

#### File Structure

```
app/agents/orchestrator/crewai/
├── __init__.py
└── crewai_orchestrator.py
```

#### Implementation Plan

1. **Convert Core Types to CrewAI Types**:
    - Map `BaseAgent` → `crewai.Agent`
    - Map `BaseTask` → `crewai.Task`
    - Handle framework-specific config via `**kwargs`

2. **Maintain Core Contracts**:
    - Preserve input/output structure defined in `BaseOrchestrator`
    - Implement validation per core interface requirements

3. **Error Handling**:
    - Convert CrewAI exceptions to `OrchestratorError`

#### File: `app/agents/orchestrator/crewai/crewai_orchestrator.py`

```
"""CrewAI implementation of BaseOrchestrator.

This module provides a concrete implementation of the orchestrator interface
using the CrewAI framework. It handles conversion between core abstractions
and CrewAI-native objects.
"""

from typing import Dict, Any, List
from crewai import Agent, Crew, Task, Process
from ...core.orchestrator import BaseOrchestrator, OrchestratorError
from ...core.agent import BaseAgent
from ...core.task import BaseTask


class CrewAIOrchestrator(BaseOrchestrator):
    """CrewAI-based workflow orchestrator."""

    def __init__(self, agents: List[BaseAgent], tasks: List[BaseTask], **kwargs):
        """
        Initialize CrewAI orchestrator.
        
        Args:
            agents: Core-compliant agents
            tasks: Core-compliant tasks
            kwargs: 
                - process: CrewAI process type (default: Process.sequential)
                - verbose: Enable verbose logging (default: False)
                - Other CrewAI Crew arguments
        """
        self.process = kwargs.pop('process', Process.sequential)
        self.verbose = kwargs.pop('verbose', False)
        super().__init__(agents, tasks, **kwargs)

    def _validate_configuration(self) -> None:
        """Validate agent/task configuration for CrewAI compatibility."""
        # 1. Check all task agents exist in agents list
        agent_ids = {id(agent) for agent in self.agents}
        for task in self.tasks:
            if id(task.agent) not in agent_ids:
                raise OrchestratorError(
                    f"Task '{task.description}' references agent not in agents list"
                )

        # 2. Verify task dependencies form valid DAG (CrewAI handles this internally)
        #    but we do basic cycle check
        dependencies = {task: task.context for task in self.tasks}
        if self._has_cycles(dependencies):
            raise OrchestratorError("Task dependencies contain cycles")

    def _has_cycles(self, dependencies: Dict[BaseTask, List[BaseTask]]) -> bool:
        """Detect cycles in task dependency graph."""
        visited = set()
        rec_stack = set()

        def dfs(task):
            visited.add(task)
            rec_stack.add(task)

            for dep in dependencies.get(task, []):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(task)
            return False

        for task in dependencies:
            if task not in visited:
                if dfs(task):
                    return True
        return False

    def kickoff(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute workflow using CrewAI.
        
        Args:
            inputs: Optional workflow inputs (passed to CrewAI's kickoff)
            
        Returns:
            {
                'result': str,  # Final output string
                'intermediate_steps': list  # [(task, output), ...]
            }
        """
        try:
            # Convert core types to CrewAI types
            crew_agents = self._create_crew_agents()
            crew_tasks = self._create_crew_tasks(crew_agents)

            # Create and execute Crew
            crew = Crew(
                agents=crew_agents,
                tasks=crew_tasks,
                process=self.process,
                verbose=self.verbose,
                **self.kwargs
            )

            result = crew.kickoff(inputs=inputs)

            # Format output per core interface
            return {
                "result": str(result),
                "intermediate_steps": [
                    (task.description, str(task_output))
                    for task, task_output in crew.tasks_outputs.items()
                ]
            }

        except Exception as e:
            raise OrchestratorError(f"CrewAI execution failed: {str(e)}") from e

    def _create_crew_agents(self) -> List[Agent]:
        """Convert BaseAgent instances to CrewAI Agent objects."""
        return [
            Agent(
                role=agent.role,
                goal=agent.goal,
                backstory=agent.backstory,
                tools=agent.tools,  # CrewAI expects tools as list[BaseTool]
                verbose=self.verbose,
                allow_delegation=False  # Delegation handled via task context
            ) for agent in self.agents
        ]

    def _create_crew_tasks(self, crew_agents: List[Agent]) -> List[Task]:
        """Convert BaseTask instances to CrewAI Task objects."""
        # Create agent mapping for quick lookup
        agent_map = {id(base_agent): crew_agent
                     for base_agent, crew_agent in zip(self.agents, crew_agents)}

        return [
            Task(
                description=task.description,
                expected_output=task.expected_output,
                agent=agent_map[id(task.agent)],
                context=[t.description for t in task.context]  # CrewAI expects descriptions
            ) for task in self.tasks
        ]
```

---

### Step 3: Documentation & Validation

#### Core Interface Guarantees

| Component          | Guarantee                                                               |
|--------------------|-------------------------------------------------------------------------|
| `BaseAgent`        | Must provide role/goal/backstory/tools - no framework-specific behavior |
| `BaseTask`         | Must define description/output/agent/dependencies - no execution logic  |
| `BaseOrchestrator` | Must implement kickoff() with standardized input/output structure       |

#### Validation Checks Implemented

1. **Agent-Task Binding**: All tasks reference valid agents
2. **Dependency Validation**: Task dependencies form acyclic graph
3. **Type Safety**: Strict type checking for core interfaces
4. **Error Standardization**: Framework-specific errors wrapped in `OrchestratorError`

#### Why This Abstraction Works

1. **Framework Isolation**:
    - Core knows nothing about CrewAI/LangChain
    - Framework implementations only depend on core interfaces
2. **Extensibility**:
    - Add LangChain by creating `langchain_orchestrator.py`
    - New frameworks only need to implement 3 ABCs
3. **Validation Safety**:
    - Core enforces basic workflow validity
    - Frameworks handle framework-specific constraints
4. **Input/Output Consistency**:
    - Standardized kickoff() signature across implementations
    - Structured result format enables consistent post-processing

---

### Next Steps for LangChain Support

1. Create `app/agents/orchestrator/langchain/langchain_orchestrator.py`
2. Implement:
   ```
   class LangChainOrchestrator(BaseOrchestrator):
       def __init__(self, agents: List[BaseAgent], tasks: List[BaseTask], **kwargs):
           # Convert core types to LangChain agents/chains
           ...
       
       def kickoff(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
           # Execute via LangChain's Runnable interface
           ...
   ```
3. Reuse all core validation logic from `BaseOrchestrator`

This design ensures new frameworks only need to implement type conversion and execution logic while inheriting robust validation and standardized interfaces from the core abstractions.
