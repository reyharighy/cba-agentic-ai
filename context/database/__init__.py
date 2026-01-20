"""
Database context for the agentic application.
"""
# internal
from .config import external_db_url
from .manager import ContextManager

__all__ = [
    "external_db_url",
    "ContextManager",
]
