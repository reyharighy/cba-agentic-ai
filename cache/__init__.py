"""
Application cache layer.

This package defines cached entry points for application-wide resources
that are initialized once and reused across the system lifecycle.
"""
# third-party
from dotenv import load_dotenv

# internal
from .context import load_database_manager
from .graph import (
    load_graph_orchestrator,
    load_prompts_set,
    load_sandbox_bootstrap,
)
from util import st_cache

@st_cache("Setting up application data and resources", "data")
def cold_start() -> None:
    """
    Initialize application-level resources.

    This function prepares shared resources required by the application
    before interactive execution begins.
    """
    load_dotenv()
    load_database_manager()
    load_graph_orchestrator()
    load_prompts_set()
    load_sandbox_bootstrap()

__all__ = [
    "cold_start",
    "load_database_manager",
    "load_graph_orchestrator",
    "load_prompts_set",
    "load_sandbox_bootstrap",
]
