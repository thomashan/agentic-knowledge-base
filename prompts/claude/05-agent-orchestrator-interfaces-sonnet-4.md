# Agentic Knowledge Base Implementation Plan

## Overview

This plan outlines the architecture for a framework-agnostic agentic knowledge base system that supports both CrewAI and LangChain orchestrators through well-defined abstractions.

## Architecture Principles

1. **Framework Agnostic Core**: All business logic resides in `app/agents/core/`
2. **Pluggable Orchestrators**: Framework-specific implementations in `app/agents/orchestrator/`
3. **Dependency Inversion**: Core depends on abstractions, orchestrators depend on core
4. **Single Responsibility**: Clear separation of concerns between orchestration and knowledge management

## Project Structure

```
agentic-knowledge-base/
│
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── abstractions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py              # Agent interface
│   │   │   │   ├── orchestrator.py       # Orchestrator interface
│   │   │   │   ├── knowledge_base.py     # Knowledge base interface
│   │   │   │   ├── task.py               # Task interface
│   │   │   │   └── workflow.py           # Workflow interface
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent_config.py       # Agent configuration models
│   │   │   │   ├── task_config.py        # Task configuration models
│   │   │   │   └── workflow_config.py    # Workflow configuration models
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── knowledge_service.py  # Knowledge management service
│   │   │   │   ├── task_service.py       # Task management service
│   │   │   │   └── workflow_service.py   # Workflow management service
│   │   │   └── exceptions/
│   │   │       ├── __init__.py
│   │   │       ├── agent_exceptions.py
│   │   │       ├── orchestrator_exceptions.py
│   │   │       └── knowledge_exceptions.py
│   │   │
│   │   └── orchestrator/
│   │       ├── __init__.py
│   │       ├── crewai/
│   │       │   ├── __init__.py
│   │       │   ├── crew_orchestrator.py  # CrewAI orchestrator implementation
│   │       │   ├── crew_agent.py         # CrewAI agent wrapper
│   │       │   └── crew_task.py          # CrewAI task wrapper
│   │       └── langchain/
│   │           ├── __init__.py
│   │           ├── lc_orchestrator.py    # LangChain orchestrator implementation
│   │           ├── lc_agent.py           # LangChain agent wrapper
│   │           └── lc_task.py            # LangChain task wrapper
```

## Implementation Phases

### Phase 1: Core Abstractions

- Define abstract base classes and interfaces
- Implement data models and configuration classes
- Create core services with business logic
- Set up exception hierarchy

### Phase 2: CrewAI Implementation

- Implement CrewAI-specific orchestrator
- Create CrewAI agent and task wrappers
- Integrate with core services
- Add CrewAI-specific configuration handling

### Phase 3: LangChain Implementation

- Implement LangChain-specific orchestrator
- Create LangChain agent and task wrappers
- Ensure compatibility with core abstractions
- Add LangChain-specific configuration handling

### Phase 4: Integration & Testing

- Create orchestrator factory for runtime selection
- Implement comprehensive test suites
- Add configuration management
- Performance optimization and monitoring

## Key Design Patterns

1. **Abstract Factory Pattern**: For creating framework-specific components
2. **Strategy Pattern**: For pluggable orchestration strategies
3. **Adapter Pattern**: For wrapping framework-specific implementations
4. **Observer Pattern**: For workflow state management and notifications
5. **Command Pattern**: For task execution and queuing

## Dependencies Management

### Core Dependencies (Minimal)

- `pydantic` for data validation
- `typing-extensions` for enhanced type hints
- `abc` for abstract base classes

### Framework-Specific Dependencies

- CrewAI: `crewai`, `langchain-core`
- LangChain: `langchain`, `langchain-community`

## Configuration Strategy

- YAML-based configuration files
- Environment variable overrides
- Runtime orchestrator selection
- Framework-specific configuration sections
- Validation through Pydantic models

## Error Handling Strategy

- Custom exception hierarchy
- Framework-agnostic error codes
- Structured error responses
- Logging and monitoring integration
- Graceful degradation patterns

## Testing Strategy

- Unit tests for core abstractions
- Integration tests for each orchestrator
- Contract tests between core and orchestrators
- Performance benchmarks
- Mock framework implementations for testing

## Success Metrics

1. **Framework Independence**: Core logic works with any orchestrator
2. **Easy Extension**: New orchestrators can be added with minimal effort
3. **Performance**: Minimal overhead from abstraction layers
4. **Maintainability**: Clear separation of concerns and documentation

-------

```
# app/agents/core/abstractions/__init__.py
"""
Core abstractions for the agentic knowledge base system.

This module provides framework-agnostic interfaces that define the contract
between the core business logic and framework-specific orchestrator implementations.
"""

from .agent import BaseAgent, AgentCapability
from .orchestrator import BaseOrchestrator, OrchestrationResult
from .knowledge_base import BaseKnowledgeBase, KnowledgeSource
from .task import BaseTask, TaskStatus, TaskResult
from .workflow import BaseWorkflow, WorkflowStatus, WorkflowResult

__all__ = [
    "BaseAgent",
    "AgentCapability", 
    "BaseOrchestrator",
    "OrchestrationResult",
    "BaseKnowledgeBase",
    "KnowledgeSource",
    "BaseTask",
    "TaskStatus",
    "TaskResult",
    "BaseWorkflow",
    "WorkflowStatus", 
    "WorkflowResult"
]


# app/agents/core/abstractions/agent.py
"""
Abstract base class for agents in the knowledge base system.

This module defines the interface that all agent implementations must follow,
ensuring consistency across different orchestration frameworks.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


class AgentCapability(Enum):
    """Enumeration of agent capabilities."""
    RESEARCH = "research"
    ANALYSIS = "analysis"  
    WRITING = "writing"
    CODING = "coding"
    REASONING = "reasoning"
    PLANNING = "planning"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"


class AgentMetadata(BaseModel):
    """Metadata about an agent instance."""
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Agent description and purpose")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    version: str = Field(default="1.0.0", description="Agent version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Classification tags")


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    This class defines the interface that framework-specific agent implementations
    must follow. It provides a consistent API for agent interaction regardless
    of the underlying orchestration framework.
    """

    def __init__(self, metadata: AgentMetadata, config: Dict[str, Any] = None):
        """
        Initialize the agent with metadata and configuration.
        
        Args:
            metadata: Agent metadata including capabilities and description
            config: Framework-specific configuration parameters
        """
        self.metadata = metadata
        self.config = config or {}
        self._is_initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the agent with necessary resources.
        
        This method should be called before the agent can execute tasks.
        Framework-specific implementations should set up any required
        connections, models, or other resources here.
        
        Raises:
            AgentInitializationError: If initialization fails
        """
        pass

    @abstractmethod  
    async def execute(self, 
                     task_description: str,
                     context: Optional[Dict[str, Any]] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Execute a task with the given description and context.
        
        Args:
            task_description: Natural language description of the task
            context: Additional context information for task execution
            **kwargs: Framework-specific execution parameters
            
        Returns:
            Dictionary containing execution results and metadata
            
        Raises:
            AgentExecutionError: If task execution fails
            AgentNotInitializedError: If agent is not properly initialized
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up agent resources.
        
        This method should be called when the agent is no longer needed
        to properly release any allocated resources.
        """
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if the agent has been properly initialized."""
        return self._is_initialized

    @property
    def agent_id(self) -> str:
        """Get the unique agent identifier."""
        return self.metadata.id

    @property
    def capabilities(self) -> List[AgentCapability]:
        """Get the list of agent capabilities."""
        return self.metadata.capabilities

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if the agent has a specific capability."""
        return capability in self.metadata.capabilities

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "metadata": self.metadata.model_dump(),
            "config": self.config,
            "is_initialized": self.is_initialized
        }


# app/agents/core/abstractions/orchestrator.py  
"""
Abstract base class for orchestrators in the knowledge base system.

This module defines the interface for orchestrating multiple agents
to complete complex workflows and knowledge management tasks.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime
from pydantic import BaseModel, Field

from .agent import BaseAgent
from .task import BaseTask
from .workflow import BaseWorkflow


class OrchestrationStatus(Enum):
    """Status of orchestration execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class OrchestrationResult(BaseModel):
    """Result of orchestration execution."""
    orchestration_id: str = Field(..., description="Unique orchestration identifier")
    status: OrchestrationStatus = Field(..., description="Final orchestration status")
    start_time: datetime = Field(..., description="Orchestration start time")
    end_time: Optional[datetime] = Field(None, description="Orchestration end time")
    results: Dict[str, Any] = Field(default_factory=dict, description="Orchestration results")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Generated artifacts")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error information if failed")


class BaseOrchestrator(ABC):
    """
    Abstract base class for orchestrating agents and workflows.
    
    This class defines the interface for managing complex multi-agent
    workflows and coordinating knowledge base operations.
    """

    def __init__(self, orchestrator_id: str, config: Dict[str, Any] = None):
        """
        Initialize the orchestrator.
        
        Args:
            orchestrator_id: Unique identifier for this orchestrator instance
            config: Framework-specific configuration parameters
        """
        self.orchestrator_id = orchestrator_id
        self.config = config or {}
        self._agents: Dict[str, BaseAgent] = {}
        self._is_initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the orchestrator and prepare for execution.
        
        This method should set up any required resources, connections,
        or framework-specific components needed for orchestration.
        
        Raises:
            OrchestratorInitializationError: If initialization fails
        """
        pass

    @abstractmethod
    async def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent instance to register
            
        Raises:
            AgentRegistrationError: If agent registration fails
        """
        pass

    @abstractmethod
    async def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the orchestrator.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Raises:
            AgentNotFoundError: If agent is not registered
        """
        pass

    @abstractmethod
    async def execute_task(self, 
                          task: BaseTask,
                          assigned_agents: Optional[List[str]] = None) -> OrchestrationResult:
        """
        Execute a single task using registered agents.
        
        Args:
            task: Task to execute
            assigned_agents: Optional list of specific agent IDs to use
            
        Returns:
            Result of task execution
            
        Raises:
            TaskExecutionError: If task execution fails
            AgentNotFoundError: If specified agents are not registered
        """
        pass

    @abstractmethod
    async def execute_workflow(self, workflow: BaseWorkflow) -> OrchestrationResult:
        """
        Execute a complete workflow with multiple tasks and agents.
        
        Args:
            workflow: Workflow to execute
            
        Returns:
            Result of workflow execution
            
        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        pass

    @abstractmethod
    async def stream_execution(self, 
                              workflow: BaseWorkflow) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a workflow and stream intermediate results.
        
        Args:
            workflow: Workflow to execute
            
        Yields:
            Intermediate execution results and status updates
            
        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        pass

    @abstractmethod
    async def pause_execution(self, orchestration_id: str) -> bool:
        """
        Pause an ongoing orchestration.
        
        Args:
            orchestration_id: ID of orchestration to pause
            
        Returns:
            True if successfully paused, False otherwise
        """
        pass

    @abstractmethod
    async def resume_execution(self, orchestration_id: str) -> bool:
        """
        Resume a paused orchestration.
        
        Args:
            orchestration_id: ID of orchestration to resume
            
        Returns:
            True if successfully resumed, False otherwise
        """
        pass

    @abstractmethod
    async def cancel_execution(self, orchestration_id: str) -> bool:
        """
        Cancel an ongoing orchestration.
        
        Args:
            orchestration_id: ID of orchestration to cancel
            
        Returns:
            True if successfully cancelled, False otherwise
        """
        pass

    @abstractmethod
    async def get_execution_status(self, orchestration_id: str) -> OrchestrationStatus:
        """
        Get the current status of an orchestration.
        
        Args:
            orchestration_id: ID of orchestration to check
            
        Returns:
            Current orchestration status
            
        Raises:
            OrchestrationNotFoundError: If orchestration ID not found
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up orchestrator resources.
        
        This method should properly shut down all agents and release
        any allocated resources.
        """
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if the orchestrator has been properly initialized."""
        return self._is_initialized

    @property
    def registered_agents(self) -> List[str]:
        """Get list of registered agent IDs."""
        return list(self._agents.keys())

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get a registered agent by ID."""
        return self._agents.get(agent_id)

    def has_agent(self, agent_id: str) -> bool:
        """Check if an agent is registered."""
        return agent_id in self._agents


# app/agents/core/abstractions/knowledge_base.py
"""
Abstract base class for knowledge base implementations.

This module defines the interface for knowledge storage, retrieval,
and management operations that support the agentic system.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeType(Enum):
    """Types of knowledge that can be stored."""
    DOCUMENT = "document"
    STRUCTURED_DATA = "structured_data"
    CONVERSATION = "conversation"
    EMBEDDING = "embedding"
    METADATA = "metadata"
    WORKFLOW_RESULT = "workflow_result"


class KnowledgeSource(BaseModel):
    """Source information for knowledge items."""
    source_id: str = Field(..., description="Unique source identifier")
    source_type: str = Field(..., description="Type of source (file, url, api, etc.)")
    source_url: Optional[str] = Field(None, description="Source URL if applicable")
    source_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional source metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeItem(BaseModel):
    """Individual knowledge item in the knowledge base."""
    item_id: str = Field(..., description="Unique item identifier")
    content: Any = Field(..., description="Knowledge content")
    knowledge_type: KnowledgeType = Field(..., description="Type of knowledge")
    source: KnowledgeSource = Field(..., description="Source information")
    tags: List[str] = Field(default_factory=list, description="Classification tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding if available")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SearchQuery(BaseModel):
    """Query for knowledge base search operations."""
    query_text: str = Field(..., description="Search query text")
    knowledge_types: Optional[List[KnowledgeType]] = Field(None, description="Filter by knowledge types")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    source_types: Optional[List[str]] = Field(None, description="Filter by source types")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filter conditions")
    max_results: int = Field(default=10, description="Maximum number of results")
    similarity_threshold: Optional[float] = Field(None, description="Minimum similarity score")


class BaseKnowledgeBase(ABC):
    """
    Abstract base class for knowledge base implementations.
    
    This class defines the interface for storing, retrieving, and managing
    knowledge that supports the agentic workflows.
    """

    def __init__(self, kb_id: str, config: Dict[str, Any] = None):
        """
        Initialize the knowledge base.
        
        Args:
            kb_id: Unique identifier for this knowledge base instance
            config: Implementation-specific configuration parameters
        """
        self.kb_id = kb_id
        self.config = config or {}
        self._is_initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the knowledge base and prepare for operations.
        
        This method should set up any required connections, indices,
        or other resources needed for knowledge base operations.
        
        Raises:
            KnowledgeBaseInitializationError: If initialization fails
        """
        pass

    @abstractmethod
    async def store_knowledge(self, item: KnowledgeItem) -> str:
        """
        Store a knowledge item in the knowledge base.
        
        Args:
            item: Knowledge item to store
            
        Returns:
            Unique identifier for the stored item
            
        Raises:
            KnowledgeStorageError: If storage operation fails
        """
        pass

    @abstractmethod
    async def retrieve_knowledge(self, item_id: str) -> Optional[KnowledgeItem]:
        """
        Retrieve a knowledge item by its ID.
        
        Args:
            item_id: Unique identifier of the item to retrieve
            
        Returns:
            Knowledge item if found, None otherwise
            
        Raises:
            KnowledgeRetrievalError: If retrieval operation fails
        """
        pass

    @abstractmethod
    async def search_knowledge(self, query: SearchQuery) -> List[KnowledgeItem]:
        """
        Search for knowledge items matching the query criteria.
        
        Args:
            query: Search query with filters and criteria
            
        Returns:
            List of matching knowledge items
            
        Raises:
            KnowledgeSearchError: If search operation fails
        """
        pass

    @abstractmethod
    async def similarity_search(self, 
                               query_embedding: List[float],
                               max_results: int = 10,
                               similarity_threshold: float = 0.7) -> List[KnowledgeItem]:
        """
        Search for knowledge items using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar knowledge items
            
        Raises:
            KnowledgeSearchError: If similarity search fails
        """
        pass

    @abstractmethod
    async def update_knowledge(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing knowledge item.
        
        Args:
            item_id: Unique identifier of the item to update
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            KnowledgeUpdateError: If update operation fails
        """
        pass

    @abstractmethod
    async def delete_knowledge(self, item_id: str) -> bool:
        """
        Delete a knowledge item from the knowledge base.
        
        Args:
            item_id: Unique identifier of the item to delete
            
        Returns:
            True if deletion successful, False otherwise
            
        Raises:
            KnowledgeDeletionError: If deletion operation fails
        """
        pass

    @abstractmethod
    async def stream_knowledge(self, 
                              query: SearchQuery) -> AsyncIterator[KnowledgeItem]:
        """
        Stream knowledge items matching the query criteria.
        
        Args:
            query: Search query with filters and criteria
            
        Yields:
            Matching knowledge items
            
        Raises:
            KnowledgeSearchError: If streaming operation fails
        """
        pass

    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics and metrics.
        
        Returns:
            Dictionary containing statistics like item counts, storage size, etc.
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up knowledge base resources.
        
        This method should properly close connections and release
        any allocated resources.
        """
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if the knowledge base has been properly initialized."""
        return self._is_initialized
```

-------

```
# app/agents/core/abstractions/task.py
"""
Abstract base class for tasks in the knowledge base system.

This module defines the interface for individual tasks that can be
executed by agents within workflows.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from .agent import AgentCapability


class TaskPriority(Enum):
    """Task execution priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Status of task execution."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskDependency(BaseModel):
    """Represents a dependency between tasks."""
    task_id: str = Field(..., description="ID of the dependent task")
    dependency_type: str = Field(default="completion", description="Type of dependency")
    required: bool = Field(default=True, description="Whether this dependency is required")


class TaskConstraint(BaseModel):
    """Constraints for task execution."""
    max_execution_time: Optional[timedelta] = Field(None, description="Maximum execution time")
    required_capabilities: List[AgentCapability] = Field(default_factory=list, description="Required agent capabilities")
    preferred_agents: List[str] = Field(default_factory=list, description="Preferred agent IDs")
    excluded_agents: List[str] = Field(default_factory=list, description="Excluded agent IDs")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")


class TaskResult(BaseModel):
    """Result of task execution."""
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Task execution status")
    assigned_agent: Optional[str] = Field(None, description="ID of assigned agent")
    start_time: Optional[datetime] = Field(None, description="Task start time")
    end_time: Optional[datetime] = Field(None, description="Task end time")
    output: Dict[str, Any] = Field(default_factory=dict, description="Task output data")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Generated artifacts")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error information if failed")
    
    @property
    def execution_duration(self) -> Optional[timedelta]:
        """Calculate task execution duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class BaseTask(ABC):
    """
    Abstract base class for tasks that can be executed by agents.
    
    This class defines the interface for individual units of work
    that agents can perform within larger workflows.
    """

    def __init__(self, 
                 task_id: str,
                 name: str,
                 description: str,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 constraints: Optional[TaskConstraint] = None,
                 dependencies: Optional[List[TaskDependency]] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialize the task.
        
        Args:
            task_id: Unique identifier for the task
            name: Human-readable task name
            description: Detailed task description
            priority: Task execution priority
            constraints: Execution constraints and requirements
            dependencies: List of task dependencies
            context: Additional context information
        """
        self.task_id = task_id
        self.name = name
        self.description = description
        self.priority = priority
        self.constraints = constraints or TaskConstraint()
        self.dependencies = dependencies or []
        self.context = context or {}
        self.status = TaskStatus.PENDING
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @abstractmethod
    async def validate(self) -> bool:
        """
        Validate the task configuration and requirements.
        
        Returns:
            True if task is valid and can be executed
            
        Raises:
            TaskValidationError: If validation fails
        """
        pass

    @abstractmethod
    async def prepare_execution(self, agent_id: str) -> Dict[str, Any]:
        """
        Prepare the task for execution by a specific agent.
        
        Args:
            agent_id: ID of the agent that will execute the task
            
        Returns:
            Dictionary containing execution parameters and context
            
        Raises:
            TaskPreparationError: If preparation fails
        """
        pass

    @abstractmethod
    async def post_execution(self, result: Dict[str, Any]) -> TaskResult:
        """
        Process the results after task execution.
        
        Args:
            result: Raw execution results from the agent
            
        Returns:
            Processed task result
            
        Raises:
            TaskPostProcessingError: If post-processing fails
        """
        pass

    def can_be_assigned_to_agent(self, agent_capabilities: List[AgentCapability]) -> bool:
        """
        Check if the task can be assigned to an agent with given capabilities.
        
        Args:
            agent_capabilities: List of agent capabilities
            
        Returns:
            True if agent can handle this task
        """
        required_caps = set(self.constraints.required_capabilities)
        available_caps = set(agent_capabilities)
        return required_caps.issubset(available_caps)

    def add_dependency(self, dependency: TaskDependency) -> None:
        """Add a dependency to this task."""
        self.dependencies.append(dependency)
        self.updated_at = datetime.utcnow()

    def remove_dependency(self, task_id: str) -> None:
        """Remove a dependency from this task."""
        self.dependencies = [dep for dep in self.dependencies if dep.task_id != task_id]
        self.updated_at = datetime.utcnow()

    def get_dependencies(self) -> List[TaskDependency]:
        """Get all dependencies for this task."""
        return self.dependencies.copy()

    def has_dependencies(self) -> bool:
        """Check if this task has any dependencies."""
        return len(self.dependencies) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "constraints": self.constraints.model_dump() if self.constraints else None,
            "dependencies": [dep.model_dump() for dep in self.dependencies],
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# app/agents/core/abstractions/workflow.py
"""
Abstract base class for workflows in the knowledge base system.

This module defines the interface for complex multi-task workflows
that coordinate multiple agents to achieve larger objectives.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Set, AsyncIterator
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import networkx as nx

from .task import BaseTask, TaskStatus, TaskResult, TaskPriority


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIALLY_COMPLETED = "partially_completed"


class WorkflowExecutionMode(Enum):
    """Workflow execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    DYNAMIC = "dynamic"


class WorkflowMetrics(BaseModel):
    """Metrics for workflow execution."""
    total_tasks: int = Field(default=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, description="Number of completed tasks")
    failed_tasks: int = Field(default=0, description="Number of failed tasks")
    cancelled_tasks: int = Field(default=0, description="Number of cancelled tasks")
    total_execution_time: Optional[timedelta] = Field(None, description="Total execution time")
    average_task_time: Optional[timedelta] = Field(None, description="Average task execution time")
    success_rate: float = Field(default=0.0, description="Task success rate")
    resource_utilization: Dict[str, float] = Field(default_factory=dict, description="Resource utilization metrics")


class WorkflowResult(BaseModel):
    """Result of workflow execution."""
    workflow_id: str = Field(..., description="Workflow identifier")
    status: WorkflowStatus = Field(..., description="Final workflow status")
    start_time: datetime = Field(..., description="Workflow start time")
    end_time: Optional[datetime] = Field(None, description="Workflow end time")
    task_results: Dict[str, TaskResult] = Field(default_factory=dict, description="Individual task results")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Workflow outputs")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Generated artifacts")
    metrics: WorkflowMetrics = Field(default_factory=WorkflowMetrics, description="Execution metrics")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error information if failed")

    @property
    def execution_duration(self) -> Optional[timedelta]:
        """Calculate workflow execution duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class BaseWorkflow(ABC):
    """
    Abstract base class for workflows that coordinate multiple tasks and agents.
    
    This class defines the interface for complex workflows that can manage
    task dependencies, execution order, and coordination between multiple agents.
    """

    def __init__(self,
                 workflow_id: str,
                 name: str,
                 description: str,
                 execution_mode: WorkflowExecutionMode = WorkflowExecutionMode.HYBRID,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 timeout: Optional[timedelta] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialize the workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable workflow name
            description: Detailed workflow description
            execution_mode: How tasks should be executed
            priority: Workflow execution priority
            timeout: Maximum execution time
            context: Additional context information
        """
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.execution_mode = execution_mode
        self.priority = priority
        self.timeout = timeout
        self.context = context or {}
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Task management
        self._tasks: Dict[str, BaseTask] = {}
        self._task_graph = nx.DiGraph()
        self._execution_order: List[List[str]] = []

    @abstractmethod
    async def validate(self) -> bool:
        """
        Validate the workflow configuration and task dependencies.
        
        Returns:
            True if workflow is valid and can be executed
            
        Raises:
            WorkflowValidationError: If validation fails
        """
        pass

    @abstractmethod
    async def prepare_execution(self) -> Dict[str, Any]:
        """
        Prepare the workflow for execution.
        
        This method should analyze task dependencies, optimize execution order,
        and prepare any required resources.
        
        Returns:
            Dictionary containing execution plan and parameters
            
        Raises:
            WorkflowPreparationError: If preparation fails
        """
        pass

    @abstractmethod
    async def execute_step(self, step_tasks: List[str]) -> Dict[str, TaskResult]:
        """
        Execute a single step of the workflow (one or more parallel tasks).
        
        Args:
            step_tasks: List of task IDs to execute in this step
            
        Returns:
            Dictionary mapping task IDs to their results
            
        Raises:
            WorkflowExecutionError: If step execution fails
        """
        pass

    @abstractmethod
    async def handle_task_failure(self, task_id: str, error: Exception) -> bool:
        """
        Handle failure of a specific task within the workflow.
        
        Args:
            task_id: ID of the failed task
            error: Exception that caused the failure
            
        Returns:
            True if workflow should continue, False if it should fail
            
        Raises:
            WorkflowErrorHandlingError: If error handling fails
        """
        pass

    @abstractmethod
    async def finalize_execution(self, task_results: Dict[str, TaskResult]) -> WorkflowResult:
        """
        Finalize workflow execution and generate final results.
        
        Args:
            task_results: Results from all executed tasks
            
        Returns:
            Final workflow result
            
        Raises:
            WorkflowFinalizationError: If finalization fails
        """
        pass

    def add_task(self, task: BaseTask) -> None:
        """
        Add a task to the workflow.
        
        Args:
            task: Task to add to the workflow
        """
        self._tasks[task.task_id] = task
        self._task_graph.add_node(task.task_id, task=task)
        
        # Add dependency edges
        for dependency in task.dependencies:
            if dependency.task_id in self._tasks:
                self._task_graph.add_edge(dependency.task_id, task.task_id)
        
        self.updated_at = datetime.utcnow()
        self._invalidate_execution_order()

    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the workflow.
        
        Args:
            task_id: ID of task to remove
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._task_graph.remove_node(task_id)
            self.updated_at = datetime.utcnow()
            self._invalidate_execution_order()

    def get_task(self, task_id: str) -> Optional[BaseTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> Dict[str, BaseTask]:
        """Get all tasks in the workflow."""
        return self._tasks.copy()

    def has_cycles(self) -> bool:
        """Check if the workflow has circular dependencies."""
        return not nx.is_directed_acyclic_graph(self._task_graph)

    def get_execution_order(self) -> List[List[str]]:
        """
        Get the optimal execution order for tasks.
        
        Returns:
            List of lists, where each inner list contains task IDs
            that can be executed in parallel.
        """
        if not self._execution_order:
            self._compute_execution_order()
        return self._execution_order

    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """
        Get tasks that are ready to execute given completed tasks.
        
        Args:
            completed_tasks: Set of task IDs that have been completed
            
        Returns:
            List of task IDs ready for execution
        """
        ready_tasks = []
        for task_id, task in self._tasks.items():
            if task_id in completed_tasks:
                continue
                
            # Check if all dependencies are satisfied
            dependencies_satisfied = True
            for dependency in task.dependencies:
                if dependency.required and dependency.task_id not in completed_tasks:
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                ready_tasks.append(task_id)
        
        return ready_tasks

    def estimate_completion_time(self) -> Optional[timedelta]:
        """
        Estimate total workflow completion time.
        
        Returns:
            Estimated completion time, or None if cannot be estimated
        """
        # This is a simple implementation - can be enhanced with more sophisticated estimation
        if not self._tasks:
            return timedelta(0)
        
        # For now, assume each task takes 1 minute on average
        # In practice, this would use historical data or task-specific estimates
        total_tasks = len(self._tasks)
        execution_steps = len(self.get_execution_order())
        
        # Estimate based on parallelization potential
        avg_task_time = timedelta(minutes=1)
        estimated_time = avg_task_time * execution_steps
        
        return estimated_time

    def get_critical_path(self) -> List[str]:
        """
        Get the critical path through the workflow.
        
        Returns:
            List of task IDs representing the critical path
        """
        try:
            # Find the longest path in the DAG
            return nx.dag_longest_path(self._task_graph)
        except nx.NetworkXError:
            # If graph has cycles or other issues, return empty path
            return []

    def _compute_execution_order(self) -> None:
        """Compute the optimal execution order for tasks."""
        if self.has_cycles():
            raise ValueError("Workflow contains circular dependencies")
        
        # Use topological sort to get execution order
        try:
            # Group tasks by their topological level
            levels = {}
            for task_id in nx.topological_sort(self._task_graph):
                # Calculate the maximum level of dependencies
                max_dep_level = -1
                for pred in self._task_graph.predecessors(task_id):
                    max_dep_level = max(max_dep_level, levels.get(pred, 0))
                levels[task_id] = max_dep_level + 1
            
            # Group tasks by level for parallel execution
            level_groups = {}
            for task_id, level in levels.items():
                if level not in level_groups:
                    level_groups[level] = []
                level_groups[level].append(task_id)
            
            # Convert to ordered list
            self._execution_order = [level_groups[level] 
                                   for level in sorted(level_groups.keys())]
        except nx.NetworkXError as e:
            raise ValueError(f"Failed to compute execution order: {e}")

    def _invalidate_execution_order(self) -> None:
        """Invalidate cached execution order."""
        self._execution_order = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "execution_mode": self.execution_mode.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "timeout": self.timeout.total_seconds() if self.timeout else None,
            "context": self.context,
            "tasks": {task_id: task.to_dict() for task_id, task in self._tasks.items()},
            "execution_order": self.get_execution_order(),
            "has_cycles": self.has_cycles(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
```

--------

```
# app/agents/core/exceptions/__init__.py
"""
Exception classes for the agentic knowledge base system.

This module provides a hierarchy of custom exceptions that provide
clear error handling and debugging information across the system.
"""

from .agent_exceptions import *
from .orchestrator_exceptions import *
from .knowledge_exceptions import *
from .workflow_exceptions import *

__all__ = [
    # Base exceptions
    "AgenticSystemError",
    
    # Agent exceptions
    "AgentError", 
    "AgentInitializationError",
    "AgentExecutionError",
    "AgentNotInitializedError",
    "AgentRegistrationError",
    "AgentNotFoundError",
    
    # Orchestrator exceptions
    "OrchestratorError",
    "OrchestratorInitializationError", 
    "TaskExecutionError",
    "WorkflowExecutionError",
    "OrchestrationNotFoundError",
    
    # Knowledge base exceptions
    "KnowledgeBaseError",
    "KnowledgeBaseInitializationError",
    "KnowledgeStorageError",
    "KnowledgeRetrievalError", 
    "KnowledgeSearchError",
    "KnowledgeUpdateError",
    "KnowledgeDeletionError",
    
    # Workflow exceptions
    "WorkflowError",
    "WorkflowValidationError",
    "WorkflowPreparationError",
    "WorkflowFinalizationError",
    "WorkflowErrorHandlingError",
    "TaskValidationError",
    "TaskPreparationError", 
    "TaskPostProcessingError"
]


# app/agents/core/exceptions/agent_exceptions.py
"""Exception classes for agent-related errors."""


class AgenticSystemError(Exception):
    """Base exception for all agentic system errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class AgentError(AgenticSystemError):
    """Base exception for agent-related errors."""
    pass


class AgentInitializationError(AgentError):
    """Raised when agent initialization fails."""
    pass


class AgentExecutionError(AgentError):
    """Raised when agent task execution fails."""
    pass


class AgentNotInitializedError(AgentError):
    """Raised when attempting to use an uninitialized agent."""
    pass


class AgentRegistrationError(AgentError):
    """Raised when agent registration fails."""
    pass


class AgentNotFoundError(AgentError):
    """Raised when requested agent is not found."""
    pass


# app/agents/core/exceptions/orchestrator_exceptions.py
"""Exception classes for orchestrator-related errors."""

from .agent_exceptions import AgenticSystemError


class OrchestratorError(AgenticSystemError):
    """Base exception for orchestrator-related errors."""
    pass


class OrchestratorInitializationError(OrchestratorError):
    """Raised when orchestrator initialization fails."""
    pass


class TaskExecutionError(OrchestratorError):
    """Raised when task execution fails."""
    pass


class WorkflowExecutionError(OrchestratorError):
    """Raised when workflow execution fails."""
    pass


class OrchestrationNotFoundError(OrchestratorError):
    """Raised when requested orchestration is not found."""
    pass


# app/agents/core/exceptions/knowledge_exceptions.py
"""Exception classes for knowledge base-related errors."""

from .agent_exceptions import AgenticSystemError


class KnowledgeBaseError(AgenticSystemError):
    """Base exception for knowledge base-related errors."""
    pass


class KnowledgeBaseInitializationError(KnowledgeBaseError):
    """Raised when knowledge base initialization fails."""
    pass


class KnowledgeStorageError(KnowledgeBaseError):
    """Raised when knowledge storage operation fails."""
    pass


class KnowledgeRetrievalError(KnowledgeBaseError):
    """Raised when knowledge retrieval operation fails."""
    pass


class KnowledgeSearchError(KnowledgeBaseError):
    """Raised when knowledge search operation fails."""
    pass


class KnowledgeUpdateError(KnowledgeBaseError):
    """Raised when knowledge update operation fails."""
    pass


class KnowledgeDeletionError(KnowledgeBaseError):
    """Raised when knowledge deletion operation fails."""
    pass


# app/agents/core/exceptions/workflow_exceptions.py
"""Exception classes for workflow and task-related errors."""

from .agent_exceptions import AgenticSystemError


class WorkflowError(AgenticSystemError):
    """Base exception for workflow-related errors."""
    pass


class WorkflowValidationError(WorkflowError):
    """Raised when workflow validation fails."""
    pass


class WorkflowPreparationError(WorkflowError):
    """Raised when workflow preparation fails."""
    pass


class WorkflowFinalizationError(WorkflowError):
    """Raised when workflow finalization fails."""
    pass


class WorkflowErrorHandlingError(WorkflowError):
    """Raised when workflow error handling fails."""
    pass


class TaskValidationError(WorkflowError):
    """Raised when task validation fails."""
    pass


class TaskPreparationError(WorkflowError):
    """Raised when task preparation fails."""
    pass


class TaskPostProcessingError(WorkflowError):
    """Raised when task post-processing fails."""
    pass


# app/agents/core/services/__init__.py
"""
Core services for the agentic knowledge base system.

This module provides framework-agnostic business logic services
that orchestrate the core functionality of the system.
"""

from .knowledge_service import KnowledgeService
from .task_service import TaskService
from .workflow_service import WorkflowService

__all__ = [
    "KnowledgeService",
    "TaskService", 
    "WorkflowService"
]


# app/agents/core/services/knowledge_service.py
"""
Service for managing knowledge base operations.

This service provides high-level operations for knowledge management
that abstract away the specific knowledge base implementation details.
"""

from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime
import logging

from ..abstractions.knowledge_base import (
    BaseKnowledgeBase, KnowledgeItem, KnowledgeSource, 
    KnowledgeType, SearchQuery
)
from ..exceptions import KnowledgeBaseError, KnowledgeStorageError


logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    High-level service for knowledge base operations.
    
    This service provides a unified interface for knowledge management
    operations that work with any knowledge base implementation.
    """

    def __init__(self, knowledge_base: BaseKnowledgeBase):
        """
        Initialize the knowledge service.
        
        Args:
            knowledge_base: Knowledge base implementation to use
        """
        self.kb = knowledge_base
        self._is_initialized = False

    async def initialize(self) -> None:
        """Initialize the knowledge service and underlying knowledge base."""
        try:
            if not self.kb.is_initialized:
                await self.kb.initialize()
            self._is_initialized = True
            logger.info(f"Knowledge service initialized with KB: {self.kb.kb_id}")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge service: {e}")
            raise KnowledgeBaseError("Knowledge service initialization failed") from e

    async def store_document(self, 
                           content: str,
                           source_info: Dict[str, Any],
                           metadata: Dict[str, Any] = None,
                           tags: List[str] = None) -> str:
        """
        Store a document in the knowledge base.
        
        Args:
            content: Document content
            source_info: Source information (type, url, etc.)
            metadata: Additional metadata
            tags: Classification tags
            
        Returns:
            Unique identifier for the stored document
        """
        try:
            source = KnowledgeSource(
                source_id=source_info.get('id', f"doc_{datetime.utcnow().timestamp()}"),
                source_type=source_info.get('type', 'document'),
                source_url=source_info.get('url'),
                source_metadata=source_info.get('metadata', {})
            )
            
            item = KnowledgeItem(
                item_id=f"item_{datetime.utcnow().timestamp()}",
                content=content,
                knowledge_type=KnowledgeType.DOCUMENT,
                source=source,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            item_id = await self.kb.store_knowledge(item)
            logger.info(f"Stored document with ID: {item_id}")
            return item_id
            
        except Exception as e:
            logger.error(f"Failed to store document: {e}")
            raise KnowledgeStorageError("Document storage failed") from e

    async def store_workflow_result(self,
                                  workflow_id: str,
                                  result_data: Dict[str, Any],
                                  metadata: Dict[str, Any] = None) -> str:
        """
        Store workflow execution results in the knowledge base.
        
        Args:
            workflow_id: ID of the workflow that generated the result
            result_data: Workflow result data
            metadata: Additional metadata
            
        Returns:
            Unique identifier for the stored result
        """
        try:
            source = KnowledgeSource(
                source_id=workflow_id,
                source_type='workflow',
                source_metadata={'workflow_id': workflow_id}
            )
            
            item = KnowledgeItem(
                item_id=f"workflow_result_{workflow_id}_{datetime.utcnow().timestamp()}",
                content=result_data,
                knowledge_type=KnowledgeType.WORKFLOW_RESULT,
                source=source,
                tags=['workflow_result'],
                metadata=metadata or {}
            )
            
            item_id = await self.kb.store_knowledge(item)
            logger.info(f"Stored workflow result with ID: {item_id}")
            return item_id
            
        except Exception as e:
            logger.error(f"Failed to store workflow result: {e}")
            raise KnowledgeStorageError("Workflow result storage failed") from e

    async def search_by_content(self, 
                               query: str,
                               knowledge_types: List[KnowledgeType] = None,
                               max_results: int = 10) -> List[KnowledgeItem]:
        """
        Search knowledge base by content similarity.
        
        Args:
            query: Search query
            knowledge_types: Filter by knowledge types
            max_results: Maximum number of results
            
        Returns:
            List of matching knowledge items
        """
        try:
            search_query = SearchQuery(
                query_text=query,
                knowledge_types=knowledge_types,
                max_results=max_results
            )
            
            results = await self.kb.search_knowledge(search_query)
            logger.info(f"Found {len(results)} items for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            raise KnowledgeBaseError("Content search failed") from e

    async def get_related_knowledge(self,
                                  item_id: str,
                                  max_results: int = 5) -> List[KnowledgeItem]:
        """
        Get knowledge items related to a specific item.
        
        Args:
            item_id: ID of the reference item
            max_results: Maximum number of related items
            
        Returns:
            List of related knowledge items
        """
        try:
            # Get the reference item
            ref_item = await self.kb.retrieve_knowledge(item_id)
            if not ref_item or not ref_item.embedding:
                return []
            
            # Find similar items using embedding
            similar_items = await self.kb.similarity_search(
                query_embedding=ref_item.embedding,
                max_results=max_results + 1  # +1 to exclude the reference item
            )
            
            # Filter out the reference item itself
            related_items = [item for item in similar_items if item.item_id != item_id][:max_results]
            
            logger.info(f"Found {len(related_items)} related items for {item_id}")
            return related_items
            
        except Exception as e:
            logger.error(f"Related knowledge search failed: {e}")
            raise KnowledgeBaseError("Related knowledge search failed") from e

    async def cleanup(self) -> None:
        """Clean up knowledge service resources."""
        try:
            if self.kb.is_initialized:
                await self.kb.cleanup()
            self._is_initialized = False
            logger.info("Knowledge service cleaned up")
        except Exception as e:
            logger.error(f"Knowledge service cleanup failed: {e}")

    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._is_initialized


# app/agents/core/services/task_service.py
"""
Service for managing task operations.

This service provides high-level operations for task management
and coordination within workflows.
"""

from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
import logging
import asyncio

from ..abstractions.task import (
    BaseTask, TaskStatus, TaskResult, TaskPriority, 
    TaskConstraint, TaskDependency
)
from ..abstractions.agent import BaseAgent, AgentCapability
from ..exceptions import TaskValidationError, TaskExecutionError


logger = logging.getLogger(__name__)


class TaskService:
    """
    High-level service for task management operations.
    
    This service provides task scheduling, dependency resolution,
    and execution coordination functionality.
    """

    def __init__(self):
        """Initialize the task service."""
        self._active_tasks: Dict[str, BaseTask] = {}
        self._task_results: Dict[str, TaskResult] = {}
        self._is_initialized = True

    async def validate_task(self, task: BaseTask) -> bool:
        """
        Validate a task for execution readiness.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid
            
        Raises:
            TaskValidationError: If validation fails
        """
        try:
            # Basic validation
            if not task.task_id or not task.name:
                raise TaskValidationError("Task must have ID and name")
            
            if not task.description:
                raise TaskValidationError("Task must have description")
            
            # Validate dependencies
            for dependency in task.dependencies:
                if not dependency.task_id:
                    raise TaskValidationError("Dependency must have task_id")
            
            # Validate constraints
            if task.constraints:
                if (task.constraints.max_execution_time and 
                    task.constraints.max_execution_time <= timedelta(0)):
                    raise TaskValidationError("Max execution time must be positive")
            
            # Call task-specific validation
            is_valid = await task.validate()
            
            logger.info(f"Task validation {'passed' if is_valid else 'failed'}: {task.task_id}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Task validation error: {e}")
            raise TaskValidationError(f"Task validation failed: {e}") from e

    async def can_assign_task(self, task: BaseTask, agent: BaseAgent) -> bool:
        """
        Check if a task can be assigned to a specific agent.
        
        Args:
            task: Task to check
            agent: Agent to check against
            
        Returns:
            True if task can be assigned to agent
        """
        try:
            # Check if agent is initialized
            if not agent.is_initialized:
                return False
            
            # Check capability requirements
            if not task.can_be_assigned_to_agent(agent.capabilities):
                return False
            
            # Check preferred/excluded agents
            if task.constraints:
                if (task.constraints.preferred_agents and 
                    agent.agent_id not in task.constraints.preferred_agents):
                    return False
                
                if agent.agent_id in task.constraints.excluded_agents:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Task assignment check failed: {e}")
            return False

    async def find_suitable_agents(self, 
                                 task: BaseTask, 
                                 available_agents: List[BaseAgent]) -> List[BaseAgent]:
        """
        Find agents suitable for executing a task.
        
        Args:
            task: Task to find agents for
            available_agents: List of available agents
            
        Returns:
            List of suitable agents, sorted by suitability
        """
        suitable_agents = []
        
        for agent in available_agents:
            if await self.can_assign_task(task, agent):
                suitable_agents.append(agent)
        
        # Sort by preference (preferred agents first)
        if task.constraints and task.constraints.preferred_agents:
            suitable_agents.sort(
                key=lambda a: 0 if a.agent_id in task.constraints.preferred_agents else 1
            )
        
        logger.info(f"Found {len(suitable_agents)} suitable agents for
```
