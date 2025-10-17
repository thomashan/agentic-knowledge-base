### **Implementation Plan: `agents-research`**

#### **1. Project Goal & Vision**

The `agents-research` project will create an intelligent, autonomous agent that conducts in-depth web research. This agent's core capability is a two-step process: **searching** for relevant sources and **scraping** the
content from those sources. It will leverage an LLM to intelligently guide this process, deciding which search results are promising enough to warrant scraping. The final output will be a curated collection of raw,
scraped text, forming the basis for all further analysis.

#### **2. Tooling Strategy**

The `ResearchAgent` is fundamentally a tool-using agent. It will be designed to work with two primary, swappable tools that conform to the `AbstractTool` interface from `agents-core`:

1. **Search Tool:** An implementation (e.g., `integration-search`) that connects to a web search API like `SearXNG`. Its job is to take a query and return a list of URLs, titles, and snippets.
2. **Scrape Tool:** An implementation (e.g., `integration-scraper`) that uses a browser automation library (like Selenium or Playwright, inspired by `AgenticSeek`). Its job is to take a URL and return the clean, textual
   content of the page.

#### **3. Core Components & Data Models**

The data models will capture the scraped content. The agent will be explicitly initialized with the two tools it requires.

**File: `app/agents-research/src/agents_research/models.py`**

```python
from pydantic import BaseModel, Field
from typing import List


class ResearchResult(BaseModel):
    """A single piece of scraped content from a URL."""
    url: str = Field(description="The source URL of the content.")
    content: str = Field(description="The scraped textual content from the URL.")


class ResearchOutput(BaseModel):
    """The consolidated output of a research task, containing multiple results."""
    topic: str = Field(description="The original research topic.")
    results: List[ResearchResult] = Field(description="A list of research results from the most relevant sources.")
```

**File: `app/agents-research/src/agents_research/research.py`**

```python
from agents_core.core import AbstractAgent, AbstractTool
from typing import List, Any
from .models import ResearchOutput


class ResearchAgent(AbstractAgent):
    """
    The ResearchAgent uses an LLM to intelligently orchestrate search and
    scraping tools to gather information from the web.
    """

    def __init__(self, llm, search_tool: AbstractTool, scrape_tool: AbstractTool):
        # Agent initialization logic, including its persona and tools.
        self.llm = llm
        self.search_tool = search_tool
        self.scrape_tool = scrape_tool
        # ... other agent setup ...
        pass

    def run_research(self, topic: str) -> ResearchOutput:
        # LLM-driven logic to search, evaluate results, and scrape content.
        pass
```

#### **4. High-Level Workflow**

1. The `ResearchAgent` receives a research `topic`.
2. It calls the `search_tool` to get an initial list of search results.
3. It uses its internal **LLM** to analyze the search results and select the most promising URLs.
4. For each promising URL, it calls the `scrape_tool` to extract the textual content.
5. The agent aggregates the scraped content into a `ResearchOutput` object and returns it.

#### **5. TDD Implementation Cycle**

**Step 1: Create Test Files (RED)**

* `app/agents-research/tests/test_models.py`
* `app/agents-research/tests/test_research_agent_unit.py`
* `app/agents-research/tests/test_research_agent_integration.py`

**Step 2: Implement `test_models.py` and Make it Pass (GREEN)**

Write tests for the `ResearchResult` and `ResearchOutput` models, then implement the models in `app/agents-research/src/agents_research/models.py`.

**Step 3: Implement Unit Tests (`test_research_agent_unit.py`) and Make them Pass (GREEN)**

Write unit tests using **mock LLM and mock tools**.

* **Test URL Selection Logic:**
    * Given a topic, configure the mock `search_tool` to return dummy search results.
    * Configure the mock `llm` to select a subset of those URLs.
    * Call `research_agent.run_research()`.
    * Assert that the `scrape_tool` is only called with the URLs selected by the mock LLM.

**Step 4: Implement Integration Tests (`test_research_agent_integration.py`) and Make them Pass (GREEN)**

Write integration tests using a **real LLM and mock tools**.

* **Test Real LLM Decision-Making:**
    * Use the `llm_factory` fixture to get a real LLM instance.
    * Use mock `search_tool` and `scrape_tool`.
    * Configure the mock `search_tool` to return a realistic set of search results for a topic (e.g., "What is CrewAI?").
    * Call `research_agent.run_research()`.
    * **Assert:**
        * The process completes and returns a valid `ResearchOutput` object.
        * The `scrape_tool` was called at least once, proving the real LLM made a decision to scrape.
        * The number of scraped URLs is less than or equal to the number of initial search results.

**Step 5: Refactor (REFACTOR)**

Once all tests pass, review and refactor the code for clarity and efficiency.
