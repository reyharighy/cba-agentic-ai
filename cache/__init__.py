"""
Application cache layer.

This package defines cached entry points for application-wide resources
that are initialized once and reused across the system lifecycle.
"""
# internal
from .agent import (
    load_graph,
    load_prompts_set,
    load_sandbox_bootstrap,
)
from .context import load_context_manager
from .language_model import load_language_models
from .memory import load_memory_manager
from util import st_cache

@st_cache("Setting up application data and resources", "data")
def cold_start() -> None:
    """
    Initialize application-level resources.

    This function prepares shared resources required by the application
    before interactive execution begins.
    """
    load_context_manager()
    load_memory_manager()
    load_language_models()
    load_graph()
    load_prompts_set()
    load_sandbox_bootstrap()

__all__ = [
    "cold_start",
    "load_context_manager",
    "load_memory_manager",
    "load_language_models",
    "load_graph",
    "load_prompts_set",
    "load_sandbox_bootstrap",
]
