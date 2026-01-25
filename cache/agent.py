"""
Cache utilities for agentic graph resources.

This module provides cached access to graph-related components
used during agent execution.
"""
# standard
from typing import (
    Dict,
    Literal,
)

# third-party
from langchain_core.language_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

# internal
from .context import load_context_manager
from .language_model import load_language_models
from .memory import load_memory_manager
from agent import (
    Graph,
    Context,
    State,
)
from context.database import ContextManager
from memory.database import MemoryManager
from util import st_cache

@st_cache("Loading graph", "resource")
def load_graph() -> CompiledStateGraph[State, Context]:
    """
    Load the agentic graph.

    This function returns a compiled graph structure used to
    coordinate agent behavior.
    """
    context_manager: ContextManager = load_context_manager()
    memory_manager: MemoryManager = load_memory_manager()
    language_models: Dict[Literal["low", "medium", "high"], BaseChatModel] = load_language_models()

    graph = Graph(context_manager, memory_manager, language_models)

    return graph.build_graph()
