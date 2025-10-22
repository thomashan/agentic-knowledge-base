from litellm import completion
import structlog

log = structlog.get_logger()

class UrlSelectionAgent:
    def __init__(self, topic: str, llm: object = None):
        self.topic = topic
        self.llm = llm

    def _call_llm(self, prompt: str) -> str:
        if not self.llm:
            # This method will be mocked in the tests.
            # In a real implementation, this would call the LLM.
            raise NotImplementedError

        messages = [{"content": prompt, "role": "user"}]
        response = completion(
            model=self.llm.model,
            messages=messages,
            base_url=self.llm.base_url,
        )
        response_content = response.choices[0].message.content
        log.info("LLM Response", response=response_content)
        return response_content

    def select_urls(self, search_results: list[dict]) -> list[str]:
        prompt = self._build_prompt(search_results)
        llm_response = self._call_llm(prompt)
        relevant_urls = self._parse_llm_response(llm_response, search_results)
        return relevant_urls

    def _build_prompt(self, search_results: list[dict]) -> str:
        url_list = "\n".join([f"{i+1}. {result['url']} - YES or NO?" for i, result in enumerate(search_results)])
        return f"Topic: {self.topic}\n\nRate each URL as relevant (YES) or not relevant (NO):\n\n{url_list}\n\nAnswer format:\n1. YES\n2. NO\n3. YES"

    def _parse_llm_response(self, llm_response: str, search_results: list[dict]) -> list[str]:
        relevant_urls = []
        for i, line in enumerate(llm_response.splitlines()):
            if "YES" in line.upper():
                if i < len(search_results):
                    relevant_urls.append(search_results[i]["url"])
        return relevant_urls

    def _build_simple_prompt(self, url: str) -> str:
        return f'Is this URL relevant to the topic "{self.topic}"?\n\nURL: https://www.google.com\nAnswer: NO\n\nURL: {url}\n\nAnswer with only YES or NO.'

    def select_urls_simple(self, search_results: list[dict]) -> list[str]:
        relevant_urls = []
        for result in search_results:
            url = result["url"]
            prompt = self._build_simple_prompt(url)
            response = self._call_llm(prompt)
            if "YES" in response.upper():
                relevant_urls.append(url)
        return relevant_urls
