from unittest.mock import Mock

import pytest
from agents_planner.models import Plan
from agents_planner.planner import PlannerAgent


@pytest.fixture
def mock_llm():
    llm = Mock()
    # Configure the mock to return a JSON string representing a plan
    plan_json = """
    {
        "goal": "Analyze the impact of Llama 3.2",
        "tasks": [
            {
                "task_id": 1,
                "description": "Research the key features and improvements of Llama 3.2.",
                "expected_output": "A summary of Llama 3.2's new features.",
                "agent": "Research Agent"
            },
            {
                "task_id": 2,
                "description": "Analyze the performance benchmarks of Llama 3.2 against other models.",
                "expected_output": "A comparative analysis of performance.",
                "agent": "Research Agent",
                "context": [1]
            },
            {
                "task_id": 3,
                "description": "Synthesize the findings into a final report.",
                "expected_output": "A full report on the impact of Llama 3.2.",
                "agent": "Intelligence Agent",
                "context": [1, 2]
            }
        ]
    }
    """
    llm.call.return_value = plan_json
    return llm


def test_planner_agent_instantiation(mock_llm):
    agent = PlannerAgent(llm=mock_llm)
    assert agent is not None


def test_planner_agent_generate_plan(mock_llm):
    agent = PlannerAgent(llm=mock_llm)
    goal = "Analyze the impact of Llama 3.2"
    plan = agent.generate_plan(goal)

    assert isinstance(plan, Plan)
    assert plan.goal == goal
    assert len(plan.tasks) == 3
    assert plan.tasks[0].agent == "Research Agent"
    assert plan.tasks[2].agent == "Intelligence Agent"
    mock_llm.call.assert_called_once()
