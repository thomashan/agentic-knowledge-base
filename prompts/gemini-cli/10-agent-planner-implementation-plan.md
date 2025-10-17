Based on my synthesis of the provided implementation prompts, here is a comprehensive implementation plan for the `agents-planner` project.

This plan focuses on creating a robust, test-driven, and modular planner that aligns with the patterns identified in the research documents.

---

### **Implementation Plan: `agents-planner`**

#### **1. Project Goal & Vision**

The `agents-planner` project will create an autonomous AI agent responsible for receiving a high-level goal and decomposing it into a structured, machine-readable plan. This plan will consist of a sequence of discrete
tasks, each assigned to a specific specialist agent (e.g., Research, Intelligence). The planner's output will serve as the primary input for the agent orchestrator (CrewAI), enabling dynamic and intelligent task
execution.

#### **2. Core Components & Data Models**

Following a Test-Driven Development (TDD) approach, we will first define the data structures that represent the core concepts of our planner. We will use Pydantic for robust data validation.

**File: `app/agents-planner/src/agents_planner/models.py`**

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class Task(BaseModel):
    """A single, discrete task to be executed by a specialist agent."""
    task_id: int = Field(description="A unique identifier for the task.")
    description: str = Field(description="A clear, specific description of the task to be performed.")
    expected_output: str = Field(description="A description of the expected output or artifact from this task.")
    agent: str = Field(description="The role of the specialist agent assigned to this task (e.g., 'Research Agent').")
    context: List[int] = Field(default_factory=list, description="A list of task_ids that this task depends on for context.")
    tools: List[str] = Field(default_factory=list, description="A list of recommended tools for the agent to use.")


class Plan(BaseModel):
    """A structured plan composed of a sequence of tasks."""
    goal: str = Field(description="The original high-level goal.")
    tasks: List[Task] = Field(description="A list of tasks that, when executed in sequence, achieve the goal.")
```

**File: `app/agents-planner/src/agents_planner/planner.py`**

```python
from agents_core.core import BaseAgent  # Assuming a BaseAgent interface exists
from .models import Plan


class PlannerAgent(BaseAgent):
    """
    The PlannerAgent uses an LLM to decompose a high-level goal
    into a structured plan of tasks.
    """

    def __init__(self, llm):
        # Agent initialization logic will go here
        # Role, goal, backstory will be set to guide the LLM
        pass

    def generate_plan(self, goal: str) -> Plan:
        # Logic to call the LLM with a specific prompt to generate the plan
        # The LLM's output will be parsed and validated into a Plan object
        pass
```

#### **3. High-Level Workflow**

1. The Orchestrator receives a high-level goal (e.g., "Research the future of AI agents").
2. The Orchestrator instantiates the `PlannerAgent`.
3. The Orchestrator calls the `planner_agent.generate_plan(goal)` method.
4. The `PlannerAgent` uses its underlying LLM, guided by a specialized system prompt, to reason about the goal and break it down into steps.
5. The LLM returns a structured response (e.g., JSON) representing the plan.
6. The `PlannerAgent` parses this response and validates it against the `Plan` Pydantic model.
7. The `PlannerAgent` returns the validated `Plan` object to the Orchestrator.
8. The Orchestrator then uses this plan to execute the tasks sequentially.

#### **4. TDD Implementation Cycle**

We will implement the `agents-planner` package by following a strict RED-GREEN-REFACTOR cycle.

**Step 1: Create Test Files (RED)**

First, I will create the necessary test files. The tests will fail initially because the implementation doesn't exist.

* **`app/agents-planner/tests/test_models.py`**: To test our Pydantic data models.
* **`app/agents-planner/tests/test_planner.py`**: To test the `PlannerAgent` itself.

**Step 2: Implement `test_models.py` and Make it Pass (GREEN)**

I will write tests to ensure our data models work as expected.

* **Test 1:** Create a `Task` object with valid data and assert its properties.
* **Test 2:** Create a `Plan` object with a list of `Task` objects and assert its structure.
* **Test 3:** Test validation by attempting to create a `Task` with missing or invalid data, asserting that a `ValidationError` is raised.

I will then write the minimal code in `app/agents-planner/src/agents_planner/models.py` to make these tests pass.

**Step 3: Implement `test_planner.py` and Make it Pass (GREEN)**

I will write tests for the agent's functionality.

* **Test 1 (Instantiation):** Test that a `PlannerAgent` can be instantiated. This will require a mock LLM object.
* **Test 2 (Plan Generation):** This is the core test.
    * Given a high-level goal (e.g., "Analyze the impact of Llama 3.2").
    * The mock LLM will be configured to return a valid JSON string representing a plan.
    * Call `planner_agent.generate_plan()`.
    * Assert that the result is a valid `Plan` object.
    * Assert that the plan contains a specific number of tasks (e.g., 3).
    * Assert that the first task is assigned to the "Research Agent" and the final task is assigned to the "Intelligence Agent".

I will then implement the `PlannerAgent` class in `app/agents-planner/src/agents_planner/planner.py`, including the logic to format a prompt for the LLM and parse its response, to make these tests pass.

**Step 4: Refactor (REFACTOR)**

Once all tests are passing, I will review the code for clarity, efficiency, and adherence to best practices, refactoring as needed while ensuring all tests remain green.

#### **5. Integration with `agents-core`**

The `PlannerAgent` will be designed to conform to the `BaseAgent` interface from the `agents-core` package. This ensures that it can be seamlessly integrated into the broader agentic system and used by any orchestrator
that understands the core abstractions. The `Plan` and `Task` data models will become part of the shared vocabulary between the planner and the orchestrator.
