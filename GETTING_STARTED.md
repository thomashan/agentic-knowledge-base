# Getting Started Guide

This guide provides instructions for setting up your local development environment and running the application.

## 1. Setting Up Your Development Environment

These steps will guide you through installing the necessary prerequisites and configuring the project.

### Step 1: Install Homebrew

Homebrew is a package manager for macOS that simplifies the installation of software. If you don't have it installed, open your terminal and run the following command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Create conda environment

We use Miniforge, a minimal installer for the `conda` environment manager, to ensure a consistent Python environment.

Run the following command to install Miniforge if it's not already installed and create a conda environment named `agentic-knowledge-base`

```bash
make activate-conda-env
```

If you are installing Miniforge for the first time, close and reopen your terminal for the changes to take effect.
After installation, you will need to activate conda environment in your shell.

```bash
conda activate agentic-knowledge-base
```

### Step 3: Install Dependencies with `uv`

Once the conda environment is active, we use `uv` to install the full set of Python packages defined in `pyproject.toml`.
`uv` is a very fast Python package installer that is compatible with `pip`.

```bash
uv sync
```

### Step 5: Set up Docker for Local LLMs

Integration tests and parts of the application rely on local Large Language Models (LLMs) served via [Ollama](https://ollama.com/), which runs in a Docker container.

1. **Install Docker Desktop**: Download and install it from the [official Docker website](https://www.docker.com/products/docker-desktop/).
2. **Start Docker**: Launch the Docker Desktop application.

The necessary Ollama container will be managed automatically by the test suite.

## 2. Running the Application and Tests

With the environment set up, you can now run the application and its test suites.

### Running Unit and Integration Tests

The easiest way to run all tests is to use the `pytest` command, which will automatically discover and run all tests in the project.
The `-n auto` flag will run tests in parallel to speed up execution.

```bash
uv sync; uv run pytest -n auto
```

To run a specific test file:

```bash
uv sync; uv run pytest <directory_or_file_path>
```

### Running the Main CLI

The primary interface for this application is a command-line tool. You can run it using the `runner` module.

```bash
python -m runner.main "Your research query here" --workflow <workflow_name>
```

Replace `"Your research query here"` with the topic you want the agent to research. The `--workflow` flag is required to select the orchestration logic to use (e.g., `full-rag`, `planner`).
