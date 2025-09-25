# app/agents/core/models.py

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TaskExecutionRecord(BaseModel):
    """A record of the output from a single task execution."""
    task_description: str = Field(..., description="The original description of the task.")
    raw_output: str = Field(..., description="The raw string output of the task.")
    structured_output: Optional[Any] = Field(None, description="Structured output, if available.")

class ExecutionResult(BaseModel):
    """
    A standardized data model for the final result of an agentic orchestration.
    This ensures a consistent output format regardless of the underlying framework.
    """
    raw_output: str = Field(..., description="The final, raw string output from the entire orchestration process.")
    structured_output: Optional[Any] = Field(None, description="The final output parsed into a structured format, if applicable.")
    task_outputs: List[TaskExecutionRecord] = Field(default_factory=list, description="A list of outputs from each individual task executed during the run.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="A dictionary containing metadata about the execution (e.g., token usage, cost, execution time).")
