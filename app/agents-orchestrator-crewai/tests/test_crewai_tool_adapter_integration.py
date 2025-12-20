import pytest
from agents_core.core import AbstractTool
from crewai import Agent, Crew, Task
from crewai_adapter.adapter import CrewAITool
from pydantic import BaseModel, Field


# 1. Define a simple AbstractTool for testing
class GreetingTool(AbstractTool):
    @property
    def name(self) -> str:
        return "Greeting Tool"

    @property
    def description(self) -> str:
        return "A tool to generate a greeting for a given name."

    def execute(self, name: str) -> str:
        return f"Hello, {name}!"

    def get_command_schemas(self) -> dict[str, type[BaseModel]] | None:
        return None


# 2. Define the Pydantic schema for the tool's arguments
class GreetingToolArgs(BaseModel):
    name: str = Field(..., description="The name of the person to greet.")


@pytest.mark.integration
def test_crewai_tool_adapter_integration(llm_factory):
    """
    Tests that the CrewAITool adapter correctly wraps an AbstractTool
    and allows a CrewAI agent to execute it with arguments.
    """
    # Arrange
    # Use a real local LLM for this integration test
    llm = llm_factory()

    # Create an instance of our simple tool
    greeting_tool = GreetingTool()

    # Wrap it with our CrewAI adapter, passing the specific args_schema
    wrapped_greeting_tool = CrewAITool(tool=greeting_tool, args_schema=GreetingToolArgs)

    # Create a CrewAI agent
    test_agent = Agent(
        role="Greeter",
        goal="Greet people accurately.",
        backstory="A friendly agent that loves to say hello.",
        tools=[wrapped_greeting_tool],
        llm=llm,
        verbose=True,
    )

    # Create a task that forces the agent to use the tool
    test_task = Task(
        description="Use the Greeting Tool to greet 'World'.",
        expected_output="The greeting 'Hello, World!'",
        agent=test_agent,
    )

    # Create and run the crew
    crew = Crew(
        agents=[test_agent],
        tasks=[test_task],
        verbose=True,
    )

    # Act
    result = crew.kickoff()

    # Assert
    assert "Hello, World!" in result.raw


if __name__ == "__main__":
    pytest.main([__file__])
