# Agentic Knowledge Base

**Autonomous AI-powered knowledge base for research and documentation**

As part of building [Agentic](https://github.com/thomashan/agentic) the research and documentation was quite slow.
To speed up the process, I built an AI-powered knowledge base that can research and document any topic.
As always, I will be dog fooding the system.

I believe this knowledge base will be a valuable resource for anyone who wants to perform research and documentation tasks more efficiently.
Currently, it is in the early stages of development, and it's not designed to be used at an enterprise scale.
But it will be helpful for managing research and documentation tasks at a personal level.

# Python Directory Structure

We use the workspace layout directory structure from [uv](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources).
```
agentic-knowledge-base
├── app
│   ├── agents-core
│   │   ├── pyproject.toml
│   │   └── src
│   │   │   └── agents
│   │   │      └── core
│   │   │           ├── __init__.py
│   │   │           └── ...
│	│	└── tests
│	│	    ├── __init__.py
│	│	    └── test_core.py
│   ├── agents-intelligence
│   │   ├── ...
│   ├── agents-knowledge
│   │   ├── ...
│   └── ...
├── pyproject.toml
├── README.md
├── uv.lock
└── src
    └── albatross
        └── main.py
```


## Gemini CLI

The `GEMINI_SYSTEM_MD` environment variable is the key to achieving advanced customisation. It instructs the Gemini CLI to source its core behavioural instructions from an external file rather than its hardcoded
defaults.

The feature is enabled by setting the `GEMINI_SYSTEM_MD` environment variable within the shell.
When the variable is set to true or 1, the CLI searches for a file named `system.md` within a `.gemini` directory at the project's
root. This approach is recommended for project-specific configurations.

We can use the files in `prompts/template/**` and can be used as a template for the `.gemini/system.md` file.
