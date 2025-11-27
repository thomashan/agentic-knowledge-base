from typing import Any

from agents_core.core import AbstractLLM
from integration_llm.ollama import OllamaLLM
from integration_llm.openai import OpenAiLLM  # New import


class LlmFactory:
    """
    A factory for creating LLM client instances based on configuration.
    """

    @staticmethod
    def create_llm(config: dict[str, Any]) -> AbstractLLM:
        """
        Creates an LLM client instance.

        Args:
            config: A dictionary containing the LLM configuration, including the 'provider'.

        Returns:
            An instance of a class that implements the AbstractLLM interface.

        Raises:
            ValueError: If the provider in the config is unknown.
        """
        provider = config.get("provider")

        if provider == "ollama":
            return OllamaLLM(model=config.get("model"), base_url=config.get("base_url"))
        elif provider == "openai":  # New provider
            return OpenAiLLM(model=config.get("model"), api_key=config.get("api_key"))
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
