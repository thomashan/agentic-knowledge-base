I want to build a self-updating RAG knowledge base using only open-source tools.

Agent framework:
The agent orchestration should be abstracted enough so we can switch out agent frameworks (i.e. agent framework-agnostic).
The agents should be autonomous (i.e. do not require handholding to perform any action).

Planner agent:
The planner agent plans how to effectively research and gather information to distill information into the documentation tool.

Research agent:
Autonomous research agents gather information from external sources.
The research agent should be able to be switched out (i.e. framework-agnostic)
The research should be able to perform web searches, drive browsers, hit APIs for gathering information.

Intelligence Agent:
Agents summarize, structure, and write findings into a documentation platform.
The intelligence agent should be able to switch between different LLM (i.e. LLM agnostic)

Knowledge agent:
A versioned, human- and machine-readable documentation platform acts as the central repository and single source of truth.
This platform stores the structured findings of the AI agents and serves as the primary data source for the RAG system, while also being fully accessible to human users for collaboration and review.
The knowledge agent should be able to look up various documentation tools to serve as the source of truth.

Documentation tool:
Humans may also write into the documentation platform.
Document level versioning (not through git).
The documentation must support content types (text, diagrams)
The documentation tool should be be able to be switched out (i.e. documentation tool agnostic).
The documentation becomes the source of truth for retrieval in RAG queries.
For each tool outline the format that is used (e.g. markdown)

Retrieval agent:
The retrieval efficiently retrieves information from the vector DB.
The vector DB should be able to be switched out (i.e. vector DB agnostic).
For search both semantic and keywords searching should be used.

Infrastructure:
The entire system runs locally or on private infrastructure.
For deployment, you come up with the recommendation, outlining pros and cons.

Give few options of each aspect and pros and cons.
Give overall recommendations for the whole system.

We are aiming for small teams for scalability.
The research agent will perform various research, from technical blog to API doc to academic papers and new agents should be spun up to perform these niche topics.
The documentation is going to be self-hosted with GUI so human can also make edits. The format is irrelevant. You should come up with the recommendations.
There is no preference for programming languages.
For met-agent orchestration prefer multi-agent communication (e.g. LangGraph, CrewAI)
For web search capability use both API and browser.
For a documentation platform, it should support structured linking between documents and visual media. There is no need for access control.

I repeat, do not use any proprietary tools like confluence.
Do not write any code.
