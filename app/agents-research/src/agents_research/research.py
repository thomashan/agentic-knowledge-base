import json
from typing import Any

from agents_core.agent_reader import AgentDefinitionReader, AgentSchema
from agents_core.core import AbstractAgent, AbstractTool
from agents_core.json_utils import to_json_object

from .models import ResearchOutput, ResearchResult


class ResearchAgent(AbstractAgent):
    """
    The ResearchAgent uses an LLM to intelligently orchestrate search and
    scraping tools to gather information from the web.
    """

    def __init__(
        self,
        llm,
        search_tool: AbstractTool,
        scrape_tool: AbstractTool,
        prompt_file: str = "agent-prompts/agents-research.md",
    ):
        self.llm = llm
        self.search_tool = search_tool
        self.scrape_tool = scrape_tool

        agent_definition = AgentDefinitionReader(AgentSchema).read_agent(prompt_file)
        self._role = agent_definition.role
        self._goal = agent_definition.goal
        self._backstory = agent_definition.backstory
        self._prompt_template = agent_definition.prompt_template

    @property
    def role(self) -> str:
        return self._role

    @property
    def goal(self) -> str:
        return self._goal

    @property
    def backstory(self) -> str:
        return self._backstory

    @property
    def prompt_template(self) -> str:
        return self._prompt_template

    @property
    def tools(self) -> list[AbstractTool] | None:
        return [self.search_tool, self.scrape_tool]

    @property
    def llm_config(self) -> dict[str, Any] | None:
        return None

    def run_research(self, topic: str, max_iterations: int = 5) -> ResearchOutput:
        history = []
        results = []
        summary = ""

        for _ in range(max_iterations):
            prompt = self._prompt_template.format(topic=topic, history=json.dumps(history))
            response_text = self.llm.call(prompt)

            try:
                action = to_json_object(response_text)
                tool_name = action.get("tool_name", "").strip()
                arguments = action.get("arguments", {})

                if tool_name == "finish":
                    summary = arguments.get("summary", "")
                    break

                if tool_name == "search_tool":
                    tool_result = self.search_tool.execute(**arguments)
                    history.append({"tool": tool_name, "arguments": arguments, "result": tool_result})
                elif tool_name == "scrape_tool":
                    tool_result = self.scrape_tool.execute(**arguments)
                    if tool_result and "Failed to scrape" not in tool_result:
                        results.append(ResearchResult(url=arguments.get("url"), content=tool_result))
                    history.append({"tool": tool_name, "arguments": arguments, "result": tool_result})
                else:
                    history.append({"tool": "invalid_tool", "arguments": arguments, "result": "Invalid tool name."})

            except (json.JSONDecodeError, AttributeError):
                history.append({"tool": "invalid_action", "result": "Invalid action format."})

        if not summary:
            # If the agent didn't finish, we can try to force a summary
            summary_prompt = f"Based on the following research history, please provide a summary of your findings:\n{json.dumps(history)}"
            summary = self.llm.call(summary_prompt)

        return ResearchOutput(topic=topic, summary=summary, results=results)
