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

Continue until ALL integration tests implemented and passing.
