import pytest
from agents_core.agent_reader import AgentDefinitionReader, AgentSchema
from pydantic import ValidationError


def __write_content(content, tmp_path, file_name):
    file_path = tmp_path / file_name
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def valid_agent_file_mistune(tmp_path):
    content = """
# Agent: Test Agent

## Role

The role of the test agent.

## Goal

The goal of the test agent.

## Backstory

The backstory of the test agent.
"""
    return __write_content(content, tmp_path, "test_agent_mistune.md")


@pytest.fixture
def invalid_agent_file_mistune(tmp_path):
    content = """
# Agent: Test Agent

## Role

The role of the test agent.

## Goal

The goal of the test agent.
"""
    return __write_content(content, tmp_path, "invalid_agent_mistune.md")


def test_read_agent_valid_file(valid_agent_file_mistune):
    reader = AgentDefinitionReader(AgentSchema)
    agent_data = reader.read_agent(valid_agent_file_mistune)
    assert agent_data.role == "The role of the test agent."
    assert agent_data.goal == "The goal of the test agent."
    assert agent_data.backstory == "The backstory of the test agent."


def test_read_agent_invalid_file(invalid_agent_file_mistune):
    reader = AgentDefinitionReader(AgentSchema)
    with pytest.raises(ValidationError):
        reader.read_agent(invalid_agent_file_mistune)
