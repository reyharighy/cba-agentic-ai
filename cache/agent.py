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

@st_cache("Loading bootsrap code for sandbox environment", "data")
def load_sandbox_bootstrap() -> Dict[Literal["descriptive", "diagnostic", "predictive", "inferential"], str]:
    """
    Load sandbox bootstrap code.

    This function provides a dictionary of initialization code for the
    sandboxed execution environment categorized based on analysis type.
    """
    pandas: str = "import pandas as pd"
    numpy: str =  "import numpy as np"
    scipy: str = "import scipy"
    sklearn: str = "import sklearn"
    df_load: str = "df = pd.read_csv('dataset.csv')"
    df_load += '\n' + "for column in df.columns:"
    df_load += '\n\t' + "if pd.api.types.is_object_dtype(df[column]):"
    df_load += '\n\t\t' + "try:"
    df_load += '\n\t\t\t' + "df[column] = pd.to_datetime(df[column])"
    df_load += '\n\t\t' + "except Exception as _:"
    df_load += '\n\t\t\t' + "pass"

    descriptive: str = pandas + '\n' + numpy + '\n' + df_load
    diagnostic: str = pandas + '\n' + numpy + '\n' + scipy + '\n' + df_load
    predictive: str = pandas + '\n' + numpy + '\n' + scipy + '\n' + df_load
    inferential: str = pandas + '\n' + numpy + '\n' + sklearn + '\n' + df_load

    return {
        "descriptive": descriptive,
        "diagnostic": diagnostic,
        "predictive": predictive,
        "inferential": inferential,
    }
