# Agent Prompts

This directory contains the prompts that are used to instruct the AI agents. The prompts are written in Markdown and can contain template variables.

## Templating

The prompts use Python's standard string formatting with curly braces (`{` and `}`) for variable substitution. In cases where a literal curly brace is needed, such as in a JSON object within the prompt, it must be
escaped by using double curly braces (`{{` and `}}`).
