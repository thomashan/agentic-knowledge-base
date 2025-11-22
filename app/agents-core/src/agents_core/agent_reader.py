from pathlib import Path

from mistune import create_markdown
from mistune.core import BlockState
from mistune.renderers.markdown import MarkdownRenderer
from pydantic import BaseModel, Field, ValidationError


class AgentSchema(BaseModel):
    role: str = Field(..., description="The role of the agent.")
    goal: str = Field(..., description="The goal of the agent.")
    backstory: str = Field(..., description="The backstory of the agent.")
    prompt_template: str = Field(default=None, description="The prompt template for the agent, if any.")


class AgentDefinitionReader:
    """A class to read agent definitions from Markdown files."""

    def __init__(self, schema: type[BaseModel]):
        self.schema = schema
        # Parser to get the AST (tokens)
        self.token_parser = create_markdown(renderer=None)
        # Renderer to turn an AST back into markdown text
        self.markdown_renderer = MarkdownRenderer()

    def _get_text_from_children(self, children):
        """Extracts the raw text from a list of child tokens."""
        text_content = []
        for child in children:
            if child.get("type") == "text":
                text_content.append(child.get("raw", ""))
            elif "children" in child:
                text_content.append(self._get_text_from_children(child["children"]))
        return "".join(text_content)

    def read_agent(self, file_path: str) -> BaseModel:
        """Reads an agent's properties from a Markdown file."""
        with Path(file_path).open() as f:
            content = f.read()

        # 1. Markdown Text -> AST
        tokens = self.token_parser(content)

        agent_data = {}
        current_field = None
        content_tokens = []

        for token in tokens:
            if token.get("type") == "heading" and token.get("attrs", {}).get("level") == 2:
                if current_field:
                    # 2. AST -> Markdown Text
                    section_content = self.markdown_renderer(content_tokens, BlockState())
                    agent_data[current_field] = section_content.strip()

                heading_text = self._get_text_from_children(token.get("children", []))
                current_field = "_".join(heading_text.lower().split())
                content_tokens = []
            else:
                content_tokens.append(token)

        if current_field:
            # 2. AST -> Markdown Text (for the last section)
            section_content = self.markdown_renderer(content_tokens, BlockState())
            agent_data[current_field] = section_content.strip()

        try:
            return self.schema(**agent_data)
        except ValidationError as e:
            raise e
