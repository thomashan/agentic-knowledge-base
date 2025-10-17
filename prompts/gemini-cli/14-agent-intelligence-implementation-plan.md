### **Implementation Plan: `agents-intelligence`**

#### **1. Project Goal & Vision**

The `agents-intelligence` project will create a specialist agent that acts as the analytical core of the system. Its primary function is to take a collection of raw, unstructured research data (provided by the
`ResearchAgent`) and transform it into a structured, synthesized report. This involves identifying key insights, summarizing the information, and formatting the output in a clean, machine-readable way, preparing it for
the next stage of the pipeline (e.g., being written to a knowledge base).

#### **2. Core Components & Data Models**

The agent's primary input will be the `ResearchOutput` from the `agents-research` package. Its output will be a new data model representing a structured report.

**File: `app/agents-intelligence/src/agents_intelligence/models.py`**

```python
from pydantic import BaseModel, Field
from typing import List
# We will depend on the models from the research agent
from agents_research.models import ResearchOutput


class KeyFinding(BaseModel):
    """A single, structured insight synthesized from the research data."""
    finding_id: int = Field(description="A unique identifier for the finding.")
    title: str = Field(description="A concise title for the key finding.")
    summary: str = Field(description="A detailed summary of the finding, including its implications.")
    citations: List[str] = Field(default_factory=list, description="A list of source URLs that support this finding.")


class IntelligenceReport(BaseModel):
    """A structured report containing synthesized insights from raw research."""
    topic: str = Field(description="The original research topic.")
    executive_summary: str = Field(description="A high-level summary of the entire research topic.")
    key_findings: List[KeyFinding] = Field(description="A list of the most important, structured findings from the research.")
```

**File: `app/agents-intelligence/src/agents_intelligence/intelligence.py`**

```python
from agents_core.core import AbstractAgent
from agents_research.models import ResearchOutput
from .models import IntelligenceReport
from typing import Any


class IntelligenceAgent(AbstractAgent):
    """
    The IntelligenceAgent uses an LLM to synthesize raw research data
    into a structured, insightful report.
    """

    def __init__(self, llm: Any):
        # Agent initialization logic, including its persona.
        pass

    def generate_report(self, research_output: ResearchOutput) -> IntelligenceReport:
        # LLM-driven logic to analyze, summarize, and structure the research data.
        pass
```

#### **3. High-Level Workflow**

1. The `IntelligenceAgent` receives a `ResearchOutput` object containing the raw text from multiple sources.
2. The agent concatenates the content from all research results into a single large text block.
3. It constructs a detailed prompt, instructing its internal **LLM** to act as a "Strategy Analyst". The prompt will ask the LLM to read the provided text, generate an executive summary, and extract a list of key
   findings with titles, summaries, and citations.
4. The prompt will strictly define the required JSON output format corresponding to the `IntelligenceReport` Pydantic model.
5. The agent calls the LLM with the consolidated text and the structured prompt.
6. The agent parses the LLM's JSON response and validates it against the `IntelligenceReport` model.
7. The agent returns the validated `IntelligenceReport` object.

#### **4. TDD Implementation Cycle**

**Step 1: Create Test Files (RED)**

* `app/agents-intelligence/tests/test_models.py`
* `app/agents-intelligence/tests/test_intelligence_agent_unit.py`
* `app/agents-intelligence/tests/test_intelligence_agent_integration.py`

**Step 2: Implement `test_models.py` and Make it Pass (GREEN)**

Write tests to validate the `KeyFinding` and `IntelligenceReport` models, then implement the models in `app/agents-intelligence/src/agents_intelligence/models.py`.

**Step 3: Implement Unit Tests (`test_intelligence_agent_unit.py`) and Make them Pass (GREEN)**

Write unit tests using a **mock LLM**.

* **Test Report Generation:**
    * Create a sample `ResearchOutput` object with mock data.
    * Configure the mock `llm` to return a valid, hardcoded JSON string representing an `IntelligenceReport`.
    * Call `intelligence_agent.generate_report()`.
    * Assert that the returned object is a valid `IntelligenceReport` and that its content matches the data from the mock LLM's response.

I will then implement the `IntelligenceAgent` class in `app/agents-intelligence/src/agents_intelligence/intelligence.py`, including the logic to format the prompt and parse the response, to make the unit tests pass.

**Step 4: Implement Integration Tests (`test_intelligence_agent_integration.py`) and Make them Pass (GREEN)**

Write an integration test using a **real LLM**.

* **Test Real LLM Synthesis:**
    * Use the `llm_factory` fixture to get a real LLM instance.
    * Create a sample `ResearchOutput` object containing a significant amount of text on a specific topic (e.g., a few paragraphs about CrewAI).
    * Call `intelligence_agent.generate_report()`.
    * **Assert:**
        * The process completes and returns a valid `IntelligenceReport` object.
        * The `executive_summary` is a non-empty string.
        * The `key_findings` list contains at least one `KeyFinding`.
        * Each finding has a non-empty `title` and `summary`.

This test validates the agent's core capability: using a real LLM to perform complex synthesis and structuring of unstructured text.

**Step 5: Refactor (REFACTOR)**

Once all tests pass, review and refactor the code for clarity, efficiency, and adherence to best practices.
