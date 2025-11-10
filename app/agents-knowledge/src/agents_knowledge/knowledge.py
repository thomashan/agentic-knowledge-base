import uuid
from typing import Any

from agents_core.core import AbstractAgent, AbstractTool
from agents_intelligence.models import IntelligenceReport
from agents_knowledge.models import KnowledgePersistenceResult
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


class KnowledgeAgent(AbstractAgent):
    """
    Agent responsible for persisting knowledge into a documentation platform and a vector database.
    This agent is a "processor" and does not use an LLM directly.
    """

    def __init__(self, documentation_tool: AbstractTool, vectordb_tool: AbstractTool, embedding_model: SentenceTransformer):
        self._documentation_tool = documentation_tool
        self._vectordb_tool = vectordb_tool
        self._embedding_model = embedding_model
        self._text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # --- Implementation of Abstract Methods ---

    @property
    def role(self) -> str:
        return "Knowledge Manager"

    @property
    def goal(self) -> str:
        return "Persist structured information into the knowledge base."

    @property
    def backstory(self) -> str:
        return "I am a meticulous archivist, responsible for taking finalized intelligence reports and ensuring they are stored correctly for both human readers and future AI retrieval."

    @property
    def prompt_template(self) -> str:
        return ""  # Not used

    @property
    def llm(self) -> Any:
        return None  # Not used

    @property
    def llm_config(self) -> dict:
        return {}  # Not used

    @property
    def tools(self) -> list[AbstractTool]:
        return [self._documentation_tool, self._vectordb_tool]

    # --- Agent's Core Logic ---

    def execute(self, report: IntelligenceReport) -> KnowledgePersistenceResult:
        """
        Executes the agent's primary function of persisting the report.
        """
        return self.persist_report(report)

    def _format_report_to_markdown(self, report: IntelligenceReport) -> str:
        """Converts the intelligence report to a markdown string."""
        lines = [
            f"# {report.topic}",
            "",
            "## Executive Summary",
            report.executive_summary,
            "",
            "## Key Findings",
        ]
        for finding in report.key_findings:
            lines.append(f"### {finding.title}")
            lines.append(finding.summary)
            if finding.citations:
                lines.append("\n**Citations:**")
                for citation in finding.citations:
                    lines.append(f"- {citation}")
            lines.append("")
        return "\\n".join(lines)

    def persist_report(self, report: IntelligenceReport) -> KnowledgePersistenceResult:
        """
        Persists the intelligence report to the documentation platform and vector database.
        """
        # 1. Format report and save to documentation platform
        markdown_content = self._format_report_to_markdown(report)
        document_url = self._documentation_tool.execute(command="create_or_update_document", title=report.topic, content=markdown_content)

        # 2. Chunk the content
        chunks = self._text_splitter.split_text(markdown_content)

        # 3. Generate embeddings for each chunk
        embeddings = self._embedding_model.encode(chunks).tolist()

        # 4. Prepare data for vector database
        chunk_ids = [str(uuid.uuid4()) for _ in chunks]
        payloads = [{"text": chunk, "document_url": document_url, "topic": report.topic} for chunk in chunks]

        # 5. Upsert vectors to the vector database
        vector_ids = self._vectordb_tool.execute(command="upsert_vectors", collection_name="knowledge_base", vectors=embeddings, payloads=payloads, ids=chunk_ids)

        # 6. Return the result
        return KnowledgePersistenceResult(document_url=document_url, vector_ids=vector_ids)
