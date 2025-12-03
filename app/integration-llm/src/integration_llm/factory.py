import os

import crewai
import requests
from agents_core.core import AbstractLLM
from crewai_adapter.adapter import CrewAILLM
from dotenv import load_dotenv


def llm_factory(model: str, base_url: str, orchestrator_type: str = "crew_ai", timeout_s: int = 300, api_key: str | None = None, **kwargs) -> AbstractLLM:
    if orchestrator_type == "crew_ai":
        crew_ai_llm = crewai.LLM(model=model, timeout_s=timeout_s, base_url=base_url, api_key=api_key, **kwargs)
        return CrewAILLM(crew_ai_llm)
    else:
        raise ValueError(f"Unsupported orchestrator type: {orchestrator_type}")


# Modified create_llm function signature and internal calls
def create_llm(provider: str = None, model: str = None, base_url: str = None, orchestrator_type: str = "crew_ai", **kwargs) -> AbstractLLM:
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
        **kwargs: Additional keyword arguments to pass to the underlying LLM factory.

    Returns:
        An instance of a class that implements the AbstractLLM interface.

    Raises:
        ValueError: If the provider is not supported or required environment variables are missing.
    """
    load_dotenv()

    provider = provider or os.getenv("LLM_PROVIDER")
    model = model or os.getenv("LLM_MODEL")
    # Prioritize argument, then environment variable for base_url
    base_url = base_url or os.getenv("LLM_BASE_URL", "http://localhost:11434")

    if not provider or not model:
        raise ValueError("LLM_PROVIDER and LLM_MODEL must be set in the environment or passed as arguments.")

    provider = provider.lower()

    if provider == "ollama":
        return llm_factory(model=model, base_url=base_url, orchestrator_type=orchestrator_type, **kwargs)

    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

        referer = os.getenv("OPENROUTER_REFERER", "https://agentic-knowledge-base.com")
        headers = {"HTTP-Referer": referer}
        return llm_factory(model, base_url="https://openrouter.ai/api/v1", api_key=api_key, orchestrator_type=orchestrator_type, extra_headers=headers, **kwargs)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def check_openrouter_health() -> bool:
    """
    Performs a health check on the OpenRouter API to verify connectivity and API key validity.

    Returns:
        bool: True if the OpenRouter API is reachable and credentials are valid, False otherwise.

    Raises:
        ValueError: If required OpenRouter environment variables are not set.
        requests.exceptions.HTTPError: For HTTP errors (e.g., 401 Unauthorized, 404 Not Found).
        requests.exceptions.ConnectionError: For network-related errors.
    """
    load_dotenv()

    base_url = os.getenv("LLM_BASE_URL")
    if not base_url:
        raise ValueError("LLM_BASE_URL environment variable is not set for OpenRouter health check.")
    if not base_url.startswith("https://openrouter.ai"):
        raise ValueError("LLM_BASE_URL must be 'https://openrouter.ai/api/v1' for OpenRouter health check.")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set for OpenRouter health check.")

    referer = os.getenv("OPENROUTER_REFERER")
    if not referer:
        raise ValueError("OPENROUTER_REFERER environment variable is not set for OpenRouter health check.")

    headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": referer}

    # OpenRouter's /models endpoint is a good way to check connectivity and auth
    check_url = f"{base_url}/models"

    try:
        response = requests.get(check_url, headers=headers, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return True
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False
    except Exception:
        return False
