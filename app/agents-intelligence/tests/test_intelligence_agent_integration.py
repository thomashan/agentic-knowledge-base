import pytest
from agents_intelligence.intelligence import IntelligenceAgent
from agents_intelligence.models import IntelligenceReport
from agents_research.models import ResearchOutput, ResearchResult


@pytest.mark.integration
def test_intelligence_agent_integration(llm_factory):
    """
    Integration test for the IntelligenceAgent with a real LLM.
    """
    # Arrange
    llm = llm_factory("gemma2:2b")
    agent = IntelligenceAgent(llm=llm)

    # Create a sample ResearchOutput with content about CrewAI
    research_output = ResearchOutput(
        topic="CrewAI",
        summary="Initial research on CrewAI.",
        results=[
            ResearchResult(
                url="https://example.com/crewai-1",
                content="CrewAI is a framework for orchestrating role-playing, autonomous AI agents. It promotes collaborative intelligence by enabling agents to work together seamlessly.",
            ),
            ResearchResult(
                url="https://example.com/crewai-2",
                content="By fostering a collaborative environment, CrewAI helps agents to break down "
                "complex tasks into smaller, manageable parts, which are then assigned to the "
                "most suitable agent for the job.",
            ),
            ResearchResult(
                url="https://example.com/crewai-3",
                content="Key features of CrewAI include role-based agent design, flexible task management, "
                "and the ability to define a clear process for agents to follow. This ensures that "
                "the multi-agent system is both effective and aligned with the user's goals.",
            ),
        ],
    )

    # Act
    report = agent.generate_report(research_output)

    # Assert
    assert isinstance(report, IntelligenceReport)
    assert report.topic == "CrewAI"
    assert report.executive_summary is not None
    assert isinstance(report.executive_summary, str)
    assert len(report.executive_summary) > 0
    assert report.key_findings is not None
    assert isinstance(report.key_findings, list)
    assert len(report.key_findings) > 0

    for finding in report.key_findings:
        assert finding.title is not None
        assert isinstance(finding.title, str)
        assert len(finding.title) > 0
        assert finding.summary is not None
        assert isinstance(finding.summary, str)
        assert len(finding.summary) > 0
