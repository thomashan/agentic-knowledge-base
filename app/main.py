import os
from app.agents.orchestrator.factory import OrchestratorFactory
from app.agents.core.abc import AbstractAgent, AbstractTool, AbstractTask
from crewai_tools import ScrapeWebsiteTool
from typing import List, Optional, Dict, Any

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
    def tools(self) -> List[AbstractTool]:
        return self._tools

    @property
    def llm_config(self) -> Optional[Dict[str, Any]]:
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
    def dependencies(self) -> Optional[List['AbstractTask']]:
        return None

def main():
    orchestrator = OrchestratorFactory().create("crewai")

    # Create a tool
    scrape_tool = ScrapeWebsiteTool()

    # Create an agent
    researcher = SimpleAgent(
        role="Senior Researcher",
        goal="Uncover groundbreaking technologies",
        backstory="You are a senior researcher at a leading tech think tank.",
        tools=[scrape_tool]
    )

    # Create a task
    task = SimpleTask(
        description="Scrape the content of 'https://www.google.com' and summarize it.",
        expected_output="A concise summary of the website content.",
        agent=researcher
    )

    orchestrator.add_agent(researcher)
    orchestrator.add_task(task)

    result = orchestrator.execute()

    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print(result.raw_output)

if __name__ == "__main__":
    main()
