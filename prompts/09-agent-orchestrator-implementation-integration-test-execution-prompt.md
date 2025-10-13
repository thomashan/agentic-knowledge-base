Read @prompts/gemini-cli/06-agent-orchestrator-interface-implementation-plan-gemini-2.5-pro.md

Task: Implement integration tests from plan

Execution requirements:
1. Work on ONE test file at a time - complete before moving to next
2. After each file, run: `uv sync; uv run pytest`
3. If tests fail:
    - Analyze error output
    - Create fix plan
    - Implement fix
    - Repeat step 2
    - If still failing: create alternative fix plan and retry
    - Continue iterating until tests pass

Constraints:
- DO NOT introduce or use `langchain` or any langchain dependencies
- Use existing project dependencies only
- For local LLM integration, use this pattern: ```python
  llm = LLM(model="ollama/qwen2.5:0.5b", base_url="http://localhost:11434")
  agent = Agent(role="Researcher", goal="Find insights", llm=llm)```

Important notes:
- Test directories do NOT have `__init__.py` files - this is intentional
- Follow existing project test structure and patterns
- If local Ollama required for tests: start with `ollama serve`
- Use Ollama model: `qwen2.5:0.5b` (smallest, fastest for testing)
- DO NOT add `[tool.uv.sources]` section to individual package pyproject.toml files

Continue until ALL integration tests implemented and passing.

# Options
(Reread the file system as the current state may have changed.)
(Continue on from the last known state.)
