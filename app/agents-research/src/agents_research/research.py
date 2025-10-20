from typing import Any

from agents_core.agent_reader import AgentDefinitionReader, AgentSchema
from agents_core.core import AbstractAgent, AbstractTool

from .models import ResearchOutput, ResearchResult, SearchResult
from .url_selection import UrlSelectionAgent


class ResearchAgent(AbstractAgent):
    """
    The ResearchAgent uses an LLM to intelligently orchestrate search and
    scraping tools to gather information from the web.
    """

    def __init__(self, llm, search_tool: AbstractTool, scrape_tool: AbstractTool, agent_file: str):
        self.llm = llm
        self.search_tool = search_tool
        self.scrape_tool = scrape_tool
        self.url_selection_agent = UrlSelectionAgent(topic="", llm=llm)
        reader = AgentDefinitionReader(AgentSchema)
        agent_data = reader.read_agent(agent_file)
        self._role = agent_data.role
        self._goal = agent_data.goal
        self._backstory = agent_data.backstory

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
    def prompt_template(self) -> None:
        return None

    @property
    def tools(self) -> list[AbstractTool] | None:
        return [self.search_tool, self.scrape_tool]

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    def run_research(self, topic: str) -> ResearchOutput:
        search_results_raw = self.search_tool.execute(query=topic)

        search_results = [SearchResult(**result) for result in search_results_raw]

        self.url_selection_agent.topic = topic
        selected_urls = self.url_selection_agent.select_urls(search_results)

        research_results = []
        for url in selected_urls:
            content = self.scrape_tool.execute(url=url)
            if content and "Failed to scrape" not in content:
                research_results.append(ResearchResult(url=url, content=content))

        return ResearchOutput(topic=topic, results=research_results)
