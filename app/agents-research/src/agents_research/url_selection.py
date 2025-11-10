from pathlib import Path

import structlog
from agents_core.core import LLMError
from agents_core.json_utils import to_json_object
from agents_research.models import SearchResult, UrlRelevanceScore
from litellm import completion

log = structlog.get_logger()


class UrlSelectionAgent:
    def __init__(self, topic: str, llm: object = None, relevance_threshold: int = 5):
        self.topic = topic
        self.llm = llm
        self.relevance_threshold = relevance_threshold
        self.prompt_template = self._load_prompt_template()

    @staticmethod
    def _load_prompt_template() -> str:
        base_path = Path(__file__).parent.parent.parent.parent.parent / "agent-prompts"
        prompt_path = base_path / "agents-research-url-selector-prompt.md"
        return prompt_path.read_text()

    def _call_llm(self, prompt: str) -> str:
        if not self.llm:
            # This method will be mocked in the tests.
            # In a real implementation, this would call the LLM.
            raise NotImplementedError

        messages = [{"content": prompt, "role": "user"}]
        try:
            response = completion(
                model=self.llm.model,
                messages=messages,
                base_url=self.llm.base_url,
            )
        except Exception as e:
            raise LLMError(f"LLM call failed: {e}") from e
        response_content = response.choices[0].message.content
        log.info("LLM Response", response=response_content)
        return response_content

    def select_urls(self, search_results: list[SearchResult]) -> list[str]:
        prompt = self._build_selection_prompt(search_results)
        # Convert the search results to a dictionary for quick lookup as LLM may return hallucinated URLs.
        search_results_dict = {value.url: value for value in search_results}
        return self._get_relevance_scores(prompt, search_results_dict)

    def _get_relevance_scores(self, prompt: str, search_results_dict: dict[str, SearchResult]) -> list[str]:
        llm_response = self._call_llm(prompt)
        try:
            relevance_scores = self._json_to_url_relevance_scores(llm_response)
            # check if all URLs are present in the relevance scores
            if not all(url in relevance_scores for url in search_results_dict):
                return self._get_relevance_scores(prompt, search_results_dict)
            if len(relevance_scores) != len(search_results_dict):
                return self._get_relevance_scores(prompt, search_results_dict)
            return [str(url) for url, relevance_score in relevance_scores.items() if float(relevance_score.relevance) >= self.relevance_threshold]
        except Exception:
            return self._get_relevance_scores(prompt, search_results_dict)

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

    def _json_to_url_relevance_scores(self, llm_response: str) -> dict[str, UrlRelevanceScore]:
        json_object: list[dict[str, str]] = to_json_object(llm_response)
        return self._list_to_dict(json_object)

    @staticmethod
    def _list_to_dict(list_of_scores: list[dict[str, str]]) -> dict[str, UrlRelevanceScore]:
        return {score["url"]: UrlRelevanceScore(url=score["url"], relevance=float(score["relevance"]), rationale=score["rationale"]) for score in list_of_scores}
