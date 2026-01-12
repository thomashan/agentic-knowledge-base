import requests
from agents_core.core import AbstractLLM


class OllamaLLM(AbstractLLM):
    """
    A concrete implementation of AbstractLLM for interacting with an Ollama server.
    """

    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def call(self, prompt: str) -> str:
        """
        Sends a prompt to the Ollama server and returns the response.
        """
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["response"]
