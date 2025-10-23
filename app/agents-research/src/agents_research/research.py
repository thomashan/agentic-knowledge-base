import re
from typing import Any

from agents_core.core import AbstractAgent, AbstractTool

from .models import ResearchOutput, ResearchResult


class ResearchAgent(AbstractAgent):
    """
    The ResearchAgent uses an LLM to intelligently orchestrate search and
    scraping tools to gather information from the web.
    """

    def __init__(self, llm, search_tool: AbstractTool, scrape_tool: AbstractTool):
        self.llm = llm
        self.search_tool = search_tool
        self.scrape_tool = scrape_tool

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
        search_results = self.search_tool.execute(query=topic)

        prompt = self._create_url_selection_prompt(topic, search_results)
        llm_response = self.llm.call(prompt)

        # Use a regex to find all URLs in the response, as the LLM might not return perfect JSON.
        selected_urls = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", llm_response)

        research_results = []
        for url in selected_urls:
            content = self.scrape_tool.execute(url=url)
            if content and "Failed to scrape" not in content:
                research_results.append(ResearchResult(url=url, content=content))

        return ResearchOutput(topic=topic, results=research_results)

    def _create_url_selection_prompt(self, topic: str, search_results: list[dict]) -> str:
        results_str = "\n".join([f"- {res['title']}: {res['snippet']} ({res['url']})" for res in search_results])

        return f"""
As a Senior Research Analyst, you have been tasked with researching the topic: '{topic}'.
You have already conducted an initial search and have the following results:

{results_str}

Based on the titles and snippets, identify the most promising URLs to investigate further.
Only select URLs that appear to be valid, real, and directly relevant to the research topic.
Exclude any URLs that are clearly placeholders, invalid, or not directly related to the topic.
You MUST only select URLs that are present in the provided search results. Do NOT introduce any new URLs.
Your response MUST be a JSON array of strings, containing only the URLs you have selected.

Example:
["http://example.com/url1", "http://example.com/url2"]

Now, provide the JSON array of the most promising URLs from the search results above.
"""
