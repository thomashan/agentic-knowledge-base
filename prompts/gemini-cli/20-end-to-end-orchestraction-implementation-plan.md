Phase 0: Deliverable Generation

The first step is to generate the implementation plan itself. The content for this plan, which I am verbally describing now, would be written to and located at the specified file path:
prompts/gemini-cli/20-end-to-end-orchestraction-implementation-plan.md. All subsequent actions are derived from this correctly located file.

Phase 1: agents-orchestrator-crewai Package

My first development focus is the agents-orchestrator-crewai package.

Cycle 1: `CrewAIOrchestrator` Instantiation

1. RED (Failing Test): I will create the test file app/agents-orchestrator-crewai/tests/test_crew_manager_unit.py. Inside, a test test_crew_manager_creation will attempt to import and instantiate
   CrewAIOrchestrator. This test will fail with a ModuleNotFoundError because the class and module do not exist.

2. GREEN (Minimal Code): To pass the test, I will create the directory app/agents-orchestrator-crewai/src/crewai/ and place an __init__.py inside it. I will then create crew_manager.py
   with a minimal CrewAIOrchestrator class definition. Finally, I will update the package's pyproject.toml to find packages in the src directory. Running the test again will result in a pass.

3. REFACTOR: The code is minimal, so no refactoring is needed.

Cycle 2: `WorkflowConfig` Instantiation

1. RED: I will create a new test file, app/agents-orchestrator-crewai/tests/test_workflow_config.py, with a test test_workflow_config_creation that attempts to instantiate a WorkflowConfig object. It will
   fail because the class doesn't exist.

2. GREEN: I will create the file workflow_config.py inside the crewai source directory. In this file, I will define WorkflowConfig as a Pydantic BaseModel with agents: list and tasks:
   list fields. I will add pydantic as a dependency in the pyproject.toml. The test will now pass.

3. REFACTOR: No refactoring is required.

Cycle 3: `CrewAIOrchestrator` Initialization with `WorkflowConfig`

1. RED: I will add a new test to test_crew_manager_unit.py. This test, test_crew_manager_initializes_crew, will use unittest.mock.patch to mock crewai.Crew. It will then check that instantiating
   CrewAIOrchestrator with a WorkflowConfig causes the crewai.Crew constructor to be called correctly. The test will fail because this logic is not yet implemented.

2. GREEN: I will modify CrewAIOrchestrator.__init__ to accept a WorkflowConfig object and use its agents and tasks attributes to instantiate crewai.Crew. The test will now pass.

3. REFACTOR: I will review the __init__ method for clarity.

Phase 2: runner Package

Next, I will work on the runner package.

Cycle 4: `Runner` Instantiation

1. RED: I will create the integration test file app/runner/tests/test_runner_integration.py. A simple test, test_runner_creation, will attempt to import and instantiate the Runner class, failing with a
   ModuleNotFoundError.

2. GREEN: I will create the directory app/runner/src/runner/, add an __init__.py, and create a runner.py file with a minimal Runner class. I will also configure its pyproject.toml to find the package in src.
   The test will pass.

3. REFACTOR: No refactoring is necessary.

Cycle 5: End-to-End Orchestration Logic

1. RED: I will write the main integration test as defined in the plan. It will instantiate real agent classes but with a mock LLM and mock tools. It will then call a run method on the Runner and assert the
   output. This test will fail because the run method and its complex orchestration logic do not exist.

2. GREEN: I will fully implement the Runner class. It will be responsible for initializing the agents and tools, creating the WorkflowConfig, instantiating the CrewAIOrchestrator, invoking its run method with the
   user's query, and returning the final result. With this logic in place, the integration test will pass.

3. REFACTOR: I will refactor the Runner class, focusing on clean dependency injection and robust error handling to ensure the code is maintainable.
