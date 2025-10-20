import pytest
from agents_research.research import ResearchAgent


@pytest.fixture
def research_agent(tmp_path):
    # Create a dummy llm
    class DummyLLM:
        def call(self, prompt):
            return '["http://example.com/url1", "http://example.com/url2"]'

    # Create dummy tools
    class DummyTool:
        def execute(self, **kwargs):
            return "dummy result"

    # Create a dummy agent file
    agent_file = tmp_path / "agents-research.md"
    agent_file.write_text("""
## Role

The role of the research agent.

## Goal

The goal of the research agent.

## Backstory

The backstory of the research agent.
""")
    return ResearchAgent(llm=DummyLLM(), search_tool=DummyTool(), scrape_tool=DummyTool(), agent_file=str(agent_file))


def test_research_agent_properties(research_agent):
    assert research_agent.role == "The role of the research agent."
    assert research_agent.goal == "The goal of the research agent."
    assert research_agent.backstory == "The backstory of the research agent."
