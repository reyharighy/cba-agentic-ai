"""
Docstring for cache
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
    Docstring for cold_start
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
