# Agentic Knowledge Base

[![Run Make](https://github.com/thomashan/agentic-knowledge-base/actions/workflows/make.yml/badge.svg)](https://github.com/thomashan/agentic-knowledge-base/actions/workflows/make.yml)
[![Test - Integration](https://github.com/thomashan/agentic-knowledge-base/actions/workflows/test-integration.yml/badge.svg)](https://github.com/thomashan/agentic-knowledge-base/actions/workflows/test-integration.yml)
[![Test- Unit](https://github.com/thomashan/agentic-knowledge-base/actions/workflows/test-unit.yml/badge.svg)](https://github.com/thomashan/agentic-knowledge-base/actions/workflows/test-unit.yml)

**Autonomous AI-powered knowledge base for research and documentation**

Built to accelerate research and documentation for [Agentic](https://github.com/thomashan/agentic), this AI-powered knowledge base automates topic research and documentation generation.
This project practices dogfooding—using the tool to build itself.

**Current Status:** Early development, optimized for personal use rather than enterprise scale.

## Python Directory Structure

Uses [uv workspace layout](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources):

```
agentic-knowledge-base/
├── app/
│   ├── agents-core/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── agents_core/
│   │           ├── __init__.py
│   │           └── core.py
│   │   └── tests/
│   │       └── test_core.py
│   │
│   ├── agents-orchestrator/
│   │   ├── crewai/
│   │   │   ├── pyproject.toml
│   │   │   └── src/
│   │   │       └── crewai_adapter/
│   │   │           └── adapter.py
│   │   │   └── tests/
│   │   │       └── ...
│   │   └── factory/
│   │       ├── pyproject.toml
│   │       └── src/
│   │           └── factory/
│   │               └── factory.py
│   │
│   └── (agents-intelligence, etc.)
│
├── pyproject.toml
├── README.md
└── uv.lock
```

## Gemini CLI Configuration

**System Customization:** Set `GEMINI_SYSTEM_MD=true` or `GEMINI_SYSTEM_MD=1` to load custom instructions from `.gemini/system.md` at project root instead of CLI defaults.

**Templates:** Use `prompts/template/**` as starting templates for `.gemini/system.md`.

**Workflow Best Practice:**

- Create a branch for experimental AI-generated code ("vibe coding")
- Cherry-pick quality changes into clean feature branches
- Submit polished PRs to `main` branch
