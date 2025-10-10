import pytest
from crewai import LLM


@pytest.fixture(scope="function")
def llm():
    """Fixture to provide a configured real LLM client for integration tests."""
    return LLM(model="ollama/qwen2.5:0.5b", base_url="http://localhost:11434")
