import pytest
from crewai import Agent, Task, Crew

def test_litellm_with_mock_llm():
    agent = Agent(
        role="Test Agent",
        goal="Test Goal",
        backstory="Test Backstory",
        llm="mock_llm"
    )
    task = Task(
        description="Test Task",
        expected_output="Test Output",
        agent=agent
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    assert result is not None
