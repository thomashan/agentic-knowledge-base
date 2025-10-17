import pytest
from agents_planner.models import Plan
from agents_planner.planner import PlannerAgent


@pytest.mark.integration
def test_planner_agent_with_real_llm(llm_factory):
    """
    Tests the PlannerAgent's ability to generate a plan using a real LLM.
    """
    # 1. Get a real LLM from the factory
    llm = llm_factory("qwen2:0.5b")

    # 2. Instantiate the PlannerAgent
    planner_agent = PlannerAgent(llm=llm)

    # 3. Define a high-level goal
    goal = "Create a comprehensive report on the current state of autonomous AI agents."

    # 4. Generate a plan
    # Note: This will make a real call to the LLM and is non-deterministic
    plan = planner_agent.generate_plan(goal)

    # 5. Validate the output
    assert isinstance(plan, Plan)
    assert plan.goal == goal
    assert len(plan.tasks) > 0

    for task in plan.tasks:
        assert isinstance(task.task_id, int)
        assert isinstance(task.description, str) and len(task.description) > 0
        assert isinstance(task.expected_output, str) and len(task.expected_output) > 0
        assert isinstance(task.agent, str) and len(task.agent) > 0
