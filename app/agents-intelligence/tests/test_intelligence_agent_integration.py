import pytest
from agents_intelligence.intelligence import IntelligenceAgent
from agents_intelligence.models import IntelligenceReport
from agents_research.models import ResearchOutput, ResearchResult


@pytest.fixture
def sample_research_output():
    return ResearchOutput(
        topic="The Role of AI in Modern Software Development",
        results=[
            ResearchResult(
                url="http://example.com/ai-in-dev",
                content=(
                    "AI is revolutionizing software development by automating tasks like code generation, testing, and debugging. AI-powered tools can significantly increase developer productivity."
                ),
            ),
            ResearchResult(
                url="http://example.com/dev-tools",
                content=(
                    "Modern development environments are increasingly integrating AI assistants. "
                    "These assistants, or agents, can provide real-time feedback, suggest code improvements, and even write entire functions."
                ),
            ),
        ],
    )


@pytest.mark.integration
def test_intelligence_agent_real_llm_synthesis(llm_factory, sample_research_output):
    """
    Tests the IntelligenceAgent's ability to synthesize a report using a real LLM.
    """
    # 1. Get a real LLM from the factory
    llm = llm_factory("qwen2:0.5b")

    # 2. Instantiate the IntelligenceAgent
    agent = IntelligenceAgent(llm=llm)

    # 3. Generate a report
    report = agent.generate_report(sample_research_output)

    # 4. Validate the output
    assert isinstance(report, IntelligenceReport)
    assert report.topic == "The Role of AI in Modern Software Development"
    assert isinstance(report.executive_summary, str) and len(report.executive_summary) > 0
    assert len(report.key_findings) > 0

    for finding in report.key_findings:
        assert isinstance(finding.finding_id, int)
        assert isinstance(finding.title, str) and len(finding.title) > 0
        assert isinstance(finding.summary, str) and len(finding.summary) > 0
