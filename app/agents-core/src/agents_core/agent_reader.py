from pathlib import Path

from mistune import create_markdown
from pydantic import BaseModel, Field, ValidationError


class AgentSchema(BaseModel):
    role: str = Field(..., description="The role of the agent.")
    goal: str = Field(..., description="The goal of the agent.")
    backstory: str = Field(..., description="The backstory of the agent.")
    prompt_template: str | None = Field(..., description="The prompt template of the agent.")


class AgentDefinitionReader:
    """A class to read agent definitions from Markdown files."""

    def __init__(self, schema: type[BaseModel]):
        self.schema = schema
        # Use create_markdown with renderer=None to get raw tokens
        self.markdown_parser = create_markdown(renderer=None)

    def _get_text_from_children(self, children):
        text_content = []
        for child in children:
            if child["type"] == "text" and "raw" in child:
                text_content.append(child["raw"])
            elif "children" in child:
                text_content.append(self._get_text_from_children(child["children"]))
        return "".join(text_content)

    def read_agent(self, file_path: str) -> BaseModel:
        """Reads an agent's properties from a Markdown file."""
        with Path(file_path).open() as f:
            content = f.read()

        # mistune.create_markdown(renderer=None).parse returns a list of tokens (dictionaries)
        tokens = self.markdown_parser(content)

        agent_data = {}
        current_field = None
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token["type"] == "heading" and token["attrs"]["level"] == 2:
                heading_text = self._get_text_from_children(token["children"])
                current_field = "_".join(heading_text.lower().split(" "))

                # Look for the next non-blank_line token for paragraph content
                j = i + 1
                while j < len(tokens) and tokens[j]["type"] == "blank_line":
                    j += 1

                if j < len(tokens) and tokens[j]["type"] == "paragraph":
                    paragraph_text = self._get_text_from_children(tokens[j]["children"])
                    agent_data[current_field] = paragraph_text.strip()
                    current_field = None  # Reset after capturing content
                i = j  # Continue iteration from the paragraph token
            i += 1

        try:
            return self.schema(**agent_data)
        except ValidationError as e:
            raise e
