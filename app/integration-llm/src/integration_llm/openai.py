import openai
from agents_core.core import AbstractLLM


class OpenAiLLM(AbstractLLM):
    """
    A concrete implementation of AbstractLLM for interacting with the OpenAI API.
    """

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def call(self, prompt: str) -> str:
        """
        Sends a prompt to the OpenAI API and returns the response.
        """
        completion = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}])
        return completion.choices[0].message.content
