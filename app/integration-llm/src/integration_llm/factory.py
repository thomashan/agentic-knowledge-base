import os
from typing import Any

import crewai
from agents_core.core import AbstractLLM
from crewai_adapter.adapter import CrewAILLM
from dotenv import load_dotenv


def _llm_factory(provider: str, model: str, base_url: str, orchestrator_type: str = "crewai", timeout_s: int | float = 300, api_key: str | None = None, **kwargs) -> AbstractLLM:
    if orchestrator_type == "crewai":
        crew_ai_llm = crewai.LLM(model=model, timeout=timeout_s, base_url=base_url, api_key=api_key, provider=provider, **kwargs)
        return CrewAILLM(crew_ai_llm)
    else:
        raise ValueError(f"Unsupported orchestrator type: {orchestrator_type}")


def create_llm(provider: str = None, model: str = None, base_url: str = None, orchestrator_type: str = "crewai", timeout_s: int | float = 300, **kwargs) -> AbstractLLM:
    """
    Creates an LLM client based on the specified provider and model,
    with configuration loaded from environment variables.

    Args:
        provider (str, optional): The LLM provider to use (e.g., 'ollama', 'openrouter').
                                  Defaults to the `LLM_PROVIDER` environment variable.
        model (str, optional): The specific model to use.
                               Defaults to the `LLM_MODEL` environment variable.
        base_url (str, optional): The base URL of the LLM API.
                                  Defaults to the `LLM_BASE_URL` environment variable.
        orchestrator_type (str, optional): The type of orchestrator to create (e.g., 'crew_ai').
                                           Defaults to 'crew_ai'.
        timeout_s (int, optional): The timeout for LLM requests, in seconds. Defaults to 300.
        **kwargs: Additional keyword arguments to pass to the underlying LLM factory.

    Returns:
        An instance of a class that implements the AbstractLLM interface.

    Raises:
        ValueError: If the provider is not supported or required environment variables are missing.
    """
    load_dotenv()

    provider = str(_check_mandatory_env_vars(provider, "LLM_PROVIDER")).lower()
    model = _check_mandatory_env_vars(model, "LLM_MODEL")
    base_url = _check_mandatory_env_vars(base_url, "LLM_BASE_URL", "http://localhost:11434")

    if provider == "ollama":
        return _llm_factory(provider=provider, model=model, base_url=base_url, orchestrator_type=orchestrator_type, timeout_s=timeout_s, **kwargs)

    elif provider == "openrouter":
        api_key = _check_mandatory_env_vars(None, "OPENROUTER_API_KEY")
        if base_url.startswith("http://localhost") or base_url.startswith("https://localhost"):
            raise ValueError("LLM_BASE_URL environment variable must be set to a valid URL.")
        referer = os.getenv("OPENROUTER_REFERER", "https://agentic-knowledge-base.com")
        headers = {"HTTP-Referer": referer}
        return _llm_factory(provider=provider, model=model, base_url=base_url, api_key=api_key, orchestrator_type=orchestrator_type, timeout_s=timeout_s, extra_headers=headers)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def _check_mandatory_env_vars(parameter: Any, env_var: str, env_var_default_value: str | None = None) -> Any:
    returned_valued = parameter or os.getenv(env_var, env_var_default_value)
    if not returned_valued:
        raise ValueError(f"{env_var} must be set in the environment or passed as arguments.")
    return returned_valued
