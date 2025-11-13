"""
Public API for the documentation package.
Exposes abstract interfaces for testing and external use.
"""

from .documentation.documentation_tool import (
    DocumentationTool,
)

__all__ = [
    "DocumentationTool",
]
