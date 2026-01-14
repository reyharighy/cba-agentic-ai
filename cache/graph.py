"""
Docstring for cache.graph
"""
# standard
from typing import Dict

# third-party
from langgraph.graph.state import CompiledStateGraph

# internal
from context import (
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
from graph import (
    Orchestrator,
    Context,
    State,
)
from util import st_cache

@st_cache("Loading graph", "resource")
def load_graph_orchestrator() -> CompiledStateGraph[State, Context]:
    """
    Docstring for load_graph_orchestrator
    
    :return: Description
    :rtype: CompiledStateGraph[State, Context, State, State]
    """
    orchestrator = Orchestrator()

    return orchestrator.build_graph()

@st_cache("Loading prompts for graph context", "data")
def load_prompts_set() -> Dict[str, str]:
    """
    Docstring for load_prompts_set
    
    :return: Description
    :rtype: Dict[str, str]
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
def load_sandbox_bootstrap() -> str:
    """
    Docstring for load_sandbox_bootstrap
    
    :return: Description
    :rtype: str
    """
    bootstrap_code: str = ""
    bootstrap_code += "import pandas as pd\n"
    bootstrap_code += "import numpy as np\n"
    bootstrap_code += "import scipy\n"
    bootstrap_code += "import sklearn\n"
    bootstrap_code += "df = pd.read_csv('dataset.csv')\n"

    return bootstrap_code
