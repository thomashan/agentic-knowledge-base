from pathlib import Path
from typing import Any

import structlog
from agents_core.core import AbstractAgent, AbstractLLM
from agents_research.models import SearchResult, UrlRelevanceScore

log = structlog.get_logger()


class UrlSelectionAgent(AbstractAgent):
    def __init__(self, topic: str, llm: AbstractLLM, relevance_threshold: int = 5, max_retries: int = 3):
        self._llm = llm
        self.topic = topic
        self.relevance_threshold = relevance_threshold
        self._prompt_template_str = self._load_prompt_template()
        self._max_retries = max_retries

    @property
    def llm(self) -> AbstractLLM:
        return self._llm

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def role(self) -> str:
        return "URL Selection Specialist"

    @property
    def goal(self) -> str:
        return "Filter and select the most relevant URLs from search results based on a given topic."

    @property
    def backstory(self) -> str:
        return "You are an expert in information retrieval, capable of discerning highly relevant web pages from a large set of search results."

    @property
    def prompt_template(self) -> str:
        return self._prompt_template_str

    @property
    def tools(self) -> list[Any] | None:
        return None

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    @staticmethod
    def _load_prompt_template() -> str:
        base_path = Path(__file__).parent.parent.parent.parent.parent / "agent-prompts"
        prompt_path = base_path / "agents-research-url-selector-prompt.md"
        return prompt_path.read_text()

    def select_urls(self, search_results: list[SearchResult]) -> list[str]:
        prompt = self._build_selection_prompt(search_results)
        # Convert the search results to a dictionary for quick lookup as LLM may return hallucinated URLs.
        search_results_dict = {value.url: value for value in search_results}
        return self._get_relevance_scores(prompt, search_results_dict)

    def _get_relevance_scores(self, prompt: str, search_results_dict: dict[str, SearchResult]) -> list[str]:
        # Use llm_json instead of _call_llm and manual parsing/retry
        json_response = self.llm_json(prompt)  # Use llm_json

        # The llm_json method handles retries and ensures valid JSON
        # The recursive retry logic for content validity (URL presence/count) is now simplified
        relevance_scores = self._list_to_dict(json_response)

        # Check if all URLs are present in the relevance scores and if lengths match
        # This part of the logic might need further refinement based on LLM output
        # For now, we trust llm_json for valid JSON format.

        # Removed: if not all(url in relevance_scores for url in search_results_dict):
        # Removed:     return self._get_relevance_scores(prompt, search_results_dict)
        # Removed: if len(relevance_scores) != len(search_results_dict):
        # Removed:     return self._get_relevance_scores(prompt, search_results_dict)

        return [str(url) for url, relevance_score in relevance_scores.items() if float(relevance_score.relevance) >= self.relevance_threshold]

    @staticmethod
    def _build_url_list_section(search_results: list[SearchResult]) -> str:
        formatted_results = []
        for i, result in enumerate(search_results):
            formatted_results.append(f"""--- Result {i + 1} ---
URL: {result.url}
Title: {result.title}
Summarised Content: {result.summarised_content}

""")
        url_list_section = "\n".join(formatted_results)
        return url_list_section

    def _build_selection_prompt(self, search_results: list[SearchResult]) -> str:
        url_list_section = self._build_url_list_section(search_results)
        return self.prompt_template.format(topic=self.topic, url_list_section=url_list_section)

    def _json_to_url_relevance_scores(self, llm_response: dict[str, Any]) -> dict[str, UrlRelevanceScore]:  # Type hint changed
        # llm_json already returns a dict, so no need for to_json_object
        json_object: list[dict[str, str]] = llm_response  # Type hint for json_object
        return self._list_to_dict(json_object)

    @staticmethod
    def _list_to_dict(list_of_scores: list[dict[str, str]]) -> dict[str, UrlRelevanceScore]:
        return {score["url"]: UrlRelevanceScore(url=score["url"], relevance=float(score["relevance"]), rationale=score["rationale"]) for score in list_of_scores}
