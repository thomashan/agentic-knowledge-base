from unittest.mock import MagicMock

from agents_planner.planner import PlannerAgent


def test_initial_properties():
    agent = PlannerAgent(llm=MagicMock())
    assert agent.role == "Expert Project Planner"
    assert agent.goal == "Decompose a high-level goal into a structured, step-by-step plan of tasks. Each task must be assigned to a specialist agent."
    assert agent.backstory == (
        "You are a world-class project planner, renowned for your ability to break "
        "down the most complex challenges into a clear, logical sequence of "
        "actionable steps.You are a master of identifying dependencies and assigning "
        "tasks to the right specialist.Your plans are the gold standard in the "
        "industry."
    )
    assert agent._prompt_template is not None
