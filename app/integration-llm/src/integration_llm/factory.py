import os
from dotenv import load_dotenv
from crewai import LLM as CrewAILLM_lib
from agents_core.core import AbstractLLM
from crewai_adapter.adapter import CrewAILLM
import requests # Import requests


def create_llm(provider: str = None, model: str = None, base_url: str = None) -> AbstractLLM:
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

    Returns:
        An instance of a class that implements the AbstractLLM interface.

    Raises:
        ValueError: If the provider is not supported or required environment variables are missing.
    """
    load_dotenv()

    provider = provider or os.getenv("LLM_PROVIDER")
    model = model or os.getenv("LLM_MODEL")
    # Prioritize argument, then environment variable for base_url
    base_url = base_url or os.getenv("LLM_BASE_URL")

    if not provider or not model:
        raise ValueError("LLM_PROVIDER and LLM_MODEL must be set in the environment or passed as arguments.")

    provider = provider.lower()

    if provider == "ollama":
        # For ollama, use the provided base_url or fall back to the default
        final_base_url = base_url or "http://localhost:11434"
        crew_llm = CrewAILLM_lib(model=f"ollama/{model}", base_url=final_base_url)
        return CrewAILLM(crew_llm)

    elif provider == "openrouter":
        if not base_url:
            raise ValueError(f"LLM_BASE_URL must be set for provider '{provider}'")

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

        referer = os.getenv("OPENROUTER_REFERER")
        if not referer:
            raise ValueError("OPENROUTER_REFERER environment variable is not set.")

        headers = {"HTTP-Referer": referer}

        crew_llm = CrewAILLM_lib(
            model=model,
            base_url=base_url,
            api_key=api_key,
            extra_headers=headers,
        )
        return CrewAILLM(crew_llm)

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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": referer
    }
    
    # OpenRouter's /models endpoint is a good way to check connectivity and auth
    check_url = f"{base_url}/models"

    try:
        response = requests.get(check_url, headers=headers, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error to OpenRouter: {e}")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error from OpenRouter: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during OpenRouter health check: {e}")
        return False
