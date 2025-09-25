import os

import pytest


@pytest.mark.integration
def test_llm_connectivity(real_llm_client):
    """
    Tests basic connectivity to the configured real LLM and verifies a simple response.
    This test will use the LLM client provided by the real_llm_client fixture.
    """
    print(f"\nTesting LLM connectivity with provider: {os.getenv('INTEGRATION_TEST_LLM_PROVIDER', 'mock')}")  # noqa: T201

    # This part needs to be adapted based on the actual LLM client's API
    # For OpenAI-like clients:
    if hasattr(real_llm_client, "chat"):
        try:
            response = real_llm_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use a placeholder model name, actual model might be configured via env
                messages=[{"role": "user", "content": "Hello, LLM!"}],
                temperature=0.7,
                max_tokens=10,
            )
            assert response.choices[0].message.content is not None
            print(f"OpenAI-like LLM response: {response.choices[0].message.content}")  # noqa: T201
        except Exception as e:
            pytest.fail(f"OpenAI-like LLM connectivity test failed: {e}")
    # For Gemini-like clients:
    elif hasattr(real_llm_client, "generate_content"):
        try:
            response = real_llm_client.generate_content("Hello, LLM!")
            assert response.text is not None
            print(f"Gemini-like LLM response: {response.text}")  # noqa: T201
        except Exception as e:
            pytest.fail(f"Gemini-like LLM connectivity test failed: {e}")
    else:
        pytest.fail("Unknown LLM client type or no suitable method found for testing connectivity.")
