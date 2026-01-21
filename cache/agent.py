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
from context.system_prompts import (
    ANALYSIS_RESPONSE,
    ANALYSIS_ORCHESTRATION,
    COMPUTATION_PLANNING,
    DATA_UNAVAILABILITY,
    DIRECT_RESPONSE,
    INTENT_COMPREHENSION,
    OBSERVATION,
    PUNT_RESPONSE,
    REQUEST_CLASSIFICATION,
    SELF_CORRECTION,
    SELF_REFLECTION,
    SUMMARIZATION,
)
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
    language_models: Dict[Literal["complex", "basic"], BaseChatModel] = load_language_models()

    graph = Graph(context_manager, memory_manager, language_models)

    return graph.build_graph()

@st_cache("Loading prompts for graph context", "data")
def load_prompts_set() -> Dict[str, str]:
    """
    Load system prompt definitions.

    This function provides access to prompt content used
    within the agentic system.
    """
    return {
        "analysis_response": ANALYSIS_RESPONSE,
        "analysis_orchestration": ANALYSIS_ORCHESTRATION,
        "computation_planning": COMPUTATION_PLANNING,
        "data_unavailability": DATA_UNAVAILABILITY,
        "direct_response": DIRECT_RESPONSE,
        "intent_comprehension": INTENT_COMPREHENSION,
        "observation": OBSERVATION,
        "punt_response": PUNT_RESPONSE,
        "request_classification": REQUEST_CLASSIFICATION,
        "self_correction": SELF_CORRECTION,
        "self_reflection": SELF_REFLECTION,
        "summarization": SUMMARIZATION,
    }

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
