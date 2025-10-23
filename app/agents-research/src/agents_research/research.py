from typing import Any

from agents_core.core import AbstractAgent, AbstractTool

from .models import ResearchOutput, ResearchResult, SearchResult
from .url_selection import UrlSelectionAgent


class ResearchAgent(AbstractAgent):
    """
    The ResearchAgent uses an LLM to intelligently orchestrate search and
    scraping tools to gather information from the web.
    """

    def __init__(self, llm, search_tool: AbstractTool, scrape_tool: AbstractTool):
        self.llm = llm
        self.search_tool = search_tool
        self.scrape_tool = scrape_tool
        self.url_selection_agent = UrlSelectionAgent(topic="", llm=llm)

    @property
    def role(self) -> str:
        return "Senior Research Analyst"

    @property
    def goal(self) -> str:
        return "To conduct thorough, unbiased, and data-driven research on any given topic."

    @property
    def backstory(self) -> str:
        return (
            "You are a master of digital investigation, known for your ability to "
            "quickly find the most relevant and trustworthy information on the web. "
            "You are skilled at sifting through noise to find the signal, and you "
            "use a combination of advanced search techniques and intelligent content "
            "analysis to build a comprehensive overview of any subject."
        )

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
