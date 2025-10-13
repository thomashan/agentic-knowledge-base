# GEMINI.md

## Project Overview

This project, `agentic-knowledge-base`, is an autonomous AI-powered knowledge base for research and documentation. It is designed to accelerate research and documentation by automating topic research and documentation generation. The project is in early development and is optimized for personal use.

The architecture is based on a system of AI agents that can be orchestrated to perform complex tasks. The core of the project is the `agents-core` package, which defines the abstract interfaces for agents, tools, tasks, and orchestrators. This allows for a pluggable architecture where different orchestration frameworks and tools can be used.

## Key Technologies

- **Orchestration**: CrewAI is the primary agent orchestration framework.
- **Vector Database**: Qdrant is used for the vector database.
- **Web Search**: SearXNG is the initial implementation for web search.
- **Web Scraper**: AgenticSeek is the initial implementation for web scraping.
- **Documentation Platform**: Outline is the chosen documentation platform.
- **LLMs**: The initial implementation will use Llama 3.2 11B for all LLMs.
- **Infrastructure**: The project is designed to run on Docker and Kubernetes.
- **Monitoring**: Grafana and Prometheus are the chosen monitoring tools.
- **Dependency Management**: `uv` is used for managing the Python workspace and dependencies.
- **Environment Management**: `conda` is used for managing the Python environment.

## Project Structure

The project is a monorepo with a workspace-style layout managed by `uv`. All the Python packages are located in the `app` directory and are installed as editable packages.

- `app/agents-core`: Defines the core abstractions for the agentic system.
- `app/agents-orchestrator-crewai`: An implementation of the orchestrator interface using CrewAI.
- `app/agents-orchestrator-langchain`: An implementation of the orchestrator interface using LangChain.
- `app/runner`: Contains the main entry point for the application.
- `docs/`: Contains documentation, including architectural decisions.
- `prompts/`: Contains prompts for the AI agents.

## Getting Started

1.  **Install Miniforge**: Follow the instructions in the `Makefile` to install `miniforge`.
2.  **Create Conda Environment**: Run `make create-conda-env` to create the `agentic-knowledge-base` conda environment.
3.  **Activate Conda Environment**: Run `conda activate agentic-knowledge-base` to activate the environment.

## Building and Running

The project is still in early development, and the main entry point in `app/runner/src/main.py` is currently a placeholder. To run the project, you would typically execute the main script:

```bash
python app/runner/src/main.py
```

## Testing

To run the tests, use `pytest`:

```bash
uv run pytest
```

The tests are located in the `tests` directory of each package in the `app` directory.

## Development Conventions

- **Linting and Formatting**: `ruff` is used for linting and formatting. To automatically fix issues, run:
  ```bash
  make fix-ruff
  ```
