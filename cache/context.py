"""
Cache utilities for application context.

This module provides cached access to context-related resources
used across different parts of the application.
"""
# standard
from typing import (
    Dict,
    Literal,
)

# internal
from context.database import (
    ContextManager,
    external_db_url,
)
from context.system_prompts import (
    INTENT_COMPREHENSION,
    REQUEST_CLASSIFICATION,
    PUNT_RESPONSE,
    ANALYTICAL_REQUIREMENT,
    DIRECT_RESPONSE,
    DATA_AVAILABILITY,
    DATA_UNAVAILABILITY_RESPONSE,
    DATA_RETRIEVAL_PLANNING,
    DATA_RETRIEVAL_PLANNING_FROM_DATA_RETRIEVAL_EXECUTION,
    DATA_RETRIEVAL_PLANNING_FROM_DATA_RETRIEVAL_OBSERVATION,
    DATA_RETRIEVAL_OBSERVATION,
    ANALYTICAL_PLANNING,
    ANALYTICAL_PLANNING_FROM_ANALYTICAL_PLAN_EXECUTION,
    ANALYTICAL_PLANNING_FROM_ANALYTICAL_PLAN_OBSERVATION,
    ANALYTICAL_PLAN_OBSERVATION,
    ANALYTICAL_RESULT,
)
from util import st_cache

@st_cache("Loading context manager", "resource")
def load_context_manager() -> ContextManager:
    """
    Load the context manager instance.

    This function provides access to the external database used by
    the system to interact with business data.
    """
    return ContextManager(external_db_url)

@st_cache("Loading prompts for graph context", "data")
def load_prompts_set() -> Dict[str, str]:
    """
    Load system prompt definitions.

    This function provides access to prompt content used
    within the agentic system.
    """
    return {
        "intent_comprehension": INTENT_COMPREHENSION,
        "request_classification": REQUEST_CLASSIFICATION,
        "punt_response": PUNT_RESPONSE,
        "analytical_requirement": ANALYTICAL_REQUIREMENT,
        "direct_response": DIRECT_RESPONSE,
        "data_availability": DATA_AVAILABILITY,
        "data_unavailability_response": DATA_UNAVAILABILITY_RESPONSE,
        "data_retrieval_planning": DATA_RETRIEVAL_PLANNING,
        "data_retrieval_planning_from_data_retrieval_execution": DATA_RETRIEVAL_PLANNING_FROM_DATA_RETRIEVAL_EXECUTION,
        "data_retrieval_planning_from_data_retrieval_observation": DATA_RETRIEVAL_PLANNING_FROM_DATA_RETRIEVAL_OBSERVATION,
        "data_retrieval_observation": DATA_RETRIEVAL_OBSERVATION,
        "analytical_planning": ANALYTICAL_PLANNING,
        "analytical_planning_from_analytical_plan_execution": ANALYTICAL_PLANNING_FROM_ANALYTICAL_PLAN_EXECUTION,
        "analytical_planning_from_analytical_observation": ANALYTICAL_PLANNING_FROM_ANALYTICAL_PLAN_OBSERVATION,
        "analytical_plan_observation": ANALYTICAL_PLAN_OBSERVATION,
        "analytical_result": ANALYTICAL_RESULT,
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
