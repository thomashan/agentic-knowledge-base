from app.agents.core.models import TaskExecutionRecord, ExecutionResult

def test_task_execution_record_instantiation():
    """Tests the instantiation of the TaskExecutionRecord model."""
    record = TaskExecutionRecord(
        task_description="Test task",
        raw_output="Test output"
    )
    assert record.task_description == "Test task"
    assert record.raw_output == "Test output"
    assert record.structured_output is None

def test_execution_result_instantiation():
    """Tests the instantiation of the ExecutionResult model."""
    result = ExecutionResult(
        raw_output="Final output"
    )
    assert result.raw_output == "Final output"
    assert result.structured_output is None
    assert result.task_outputs == []
    assert result.metadata == {}
