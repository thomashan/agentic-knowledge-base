"""
Public API for the integration_documentation package.
Exposes abstract interfaces and models for testing and external use.
"""

from .documentation.documentation_tool import DocumentationTool

__all__ = [
    "DocumentationTool",
]
