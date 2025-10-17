from pydantic import BaseModel, Field


class Task(BaseModel):
    """A single, discrete task to be executed by a specialist agent."""

    task_id: int = Field(description="A unique identifier for the task.")
    description: str = Field(description="A clear, specific description of the task to be performed.")
    expected_output: str = Field(description="A description of the expected output or artifact from this task.")
    agent: str = Field(description="The role of the specialist agent assigned to this task (e.g., 'Research Agent').")
    context: list[int] = Field(default_factory=list, description="A list of task_ids that this task depends on for context.")
    tools: list[str] = Field(default_factory=list, description="A list of recommended tools for the agent to use.")


class Plan(BaseModel):
    """A structured plan composed of a sequence of tasks."""

    goal: str = Field(description="The original high-level goal.")
    tasks: list[Task] = Field(description="A list of tasks that, when executed in sequence, achieve the goal.")
