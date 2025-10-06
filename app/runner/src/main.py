from typing import Any

from agents.core.core import AbstractAgent, AbstractTask, AbstractTool
from app.agents.orchestrator.factory import OrchestratorFactory
from crewai_tools import ScrapeWebsiteTool

# Set up the environment for the LLM
# You need to set the OPENAI_API_KEY environment variable to run this script.
# For example:
# export OPENAI_API_KEY="YOUR_API_KEY"


class SimpleAgent(AbstractAgent):
    def __init__(self, role, goal, backstory, tools):
        self._role = role
        self._goal = goal
        self._backstory = backstory
        self._tools = tools

    @property
    def role(self) -> str:
        return self._role

    @property
    def goal(self) -> str:
        return self._goal

    @property
    def backstory(self) -> str:
        return self._backstory

    @property
    def tools(self) -> list[AbstractTool]:
        return self._tools

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None


class SimpleTask(AbstractTask):
    def __init__(self, description, expected_output, agent):
        self._description = description
        self._expected_output = expected_output
        self._agent = agent

    @property
    def description(self) -> str:
        return self._description

    @property
    def expected_output(self) -> str:
        return self._expected_output

    @property
    def agent(self) -> AbstractAgent:
        return self._agent

    @property
    def dependencies(self) -> list["AbstractTask"] | None:
        return None


def main():
    orchestrator = OrchestratorFactory().create("crewai")

    # Create a tool
    scrape_tool = ScrapeWebsiteTool()

    # Create an agent
    researcher = SimpleAgent(role="Senior Researcher", goal="Uncover groundbreaking technologies", backstory="You are a senior researcher at a leading tech think tank.", tools=[scrape_tool])

    # Create a task
    task = SimpleTask(description="Scrape the content of 'https://www.google.com' and summarize it.", expected_output="A concise summary of the website content.", agent=researcher)

    orchestrator.add_agent(researcher)
    orchestrator.add_task(task)

    result = orchestrator.execute()

    print("\n\n########################")  # noqa: T201
    print("## Here is the result")  # noqa: T201
    print("########################\n")  # noqa: T201
    print(result.raw_output)  # noqa: T201


if __name__ == "__main__":
    main()
