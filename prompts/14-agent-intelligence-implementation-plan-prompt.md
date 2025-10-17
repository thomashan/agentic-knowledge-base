**Title:** Implementation Plan for `agents-intelligence`

**Persona:** You are Gemini, an expert TDD Software Engineer.

**Context:** The `integration-llm`, `agents-orchestrator-crewai`, `agents-planner`, and `agents-research` components are complete and tested. The next component to be built is `agents-intelligence`.

**Goal:** Create a comprehensive, test-driven implementation plan for the `agents-intelligence` package.

**Input Documents:**
Analyze and synthesize the common patterns and approaches for an "Intelligence Agent" from the following documents:

* `prompts/chatgpt/02-initial-implementation-deep-research.md`
* `prompts/claude/02-initial-implementation-opus-4.1.md`
* `prompts/copilot/02-initial-implementation-smart.md`
* `prompts/deepseek/02-initial-implementation-deepthink.md`
* `prompts/gemini/02-initial-implementation-gemini-2.5-pro-deep-research.md`
* `prompts/grok/02-initial-implementation-expert.md`
* `prompts/qwen/02-initial-implementation-qwen3-235b-a22b-2507.md`

**Deliverable:**
A single markdown file containing the complete implementation plan.

**Acceptance Criteria for the Plan:**

1. The plan must define the **Goal and Vision** for the `IntelligenceAgent`. Based on the input documents, its primary role is to take raw research data and synthesize it into structured, summarized insights.
2. The plan must define the **Core Components and Data Models** using Pydantic. This should include a data model for the input (e.g., `ResearchOutput` from the `agents-research` package) and the output (e.g.,
   `IntelligenceReport`).
3. The plan must outline the **High-Level Workflow** of the agent.
4. The plan must detail a **TDD Implementation Cycle** (RED-GREEN-REFACTOR):
    * Specify the test files to be created (unit and integration).
    * Describe the tests for the data models.
    * Describe the unit tests for the agent's logic, using mock dependencies.
    * Describe the **integration test** for the agent, which must use a **real LLM** (via the `llm_factory` fixture) to validate its synthesis capabilities.
5. The plan must adhere to all **existing project conventions** (e.g., use of `AbstractAgent`, dependency injection for tools/LLMs).
6. The final plan must be written to the file: `prompts/gemini-cli/14-agent-intelligence-implementation-plan.md`.
