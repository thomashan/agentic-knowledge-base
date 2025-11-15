import pytest
from agents_planner.models import Plan, Task
from pydantic import ValidationError


def test_create_task_with_valid_data():
    task = Task(
        task_id=1,
        description="Test task",
        expected_output="Test output",
        agent="Test Agent",
    )
    assert task.task_id == 1
    assert task.description == "Test task"
    assert task.agent == "Test Agent"
    assert task.context == []
    assert task.tools == []


def test_create_plan_with_valid_data():
    task1 = Task(task_id=1, description="Task 1", expected_output="Output 1", agent="Agent 1")
    task2 = Task(task_id=2, description="Task 2", expected_output="Output 2", agent="Agent 2", context=[1])
    plan = Plan(goal="Test goal", tasks=[task1, task2])
    assert plan.goal == "Test goal"
    assert len(plan.tasks) == 2
    assert plan.tasks[0] == task1


def test_task_validation_error():
    with pytest.raises(ValidationError):
        Task(description="Invalid task")  # Missing required fields

if __name__ == "__main__":
    pytest.main()
