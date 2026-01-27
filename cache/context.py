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
    INFOGRAPHIC_REQUIREMENT,
    ANALYTICAL_RESPONSE,
    INFOGRAPHIC_PLANNING,
    INFOGRAPHIC_PLANNING_FROM_INFOGRAPHIC_PLAN_EXECUTION,
    INFOGRAPHIC_PLANNING_FROM_INFOGRAPHIC_PLAN_OBSERVATION,
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
        "analytical_planning_from_analytical_plan_observation": ANALYTICAL_PLANNING_FROM_ANALYTICAL_PLAN_OBSERVATION,
        "analytical_plan_observation": ANALYTICAL_PLAN_OBSERVATION,
        "analytical_result": ANALYTICAL_RESULT,
        "infographic_requirement": INFOGRAPHIC_REQUIREMENT,
        "analytical_response": ANALYTICAL_RESPONSE,
        "infographic_planning": INFOGRAPHIC_PLANNING,
        "infographic_planning_from_infographic_plan_execution": INFOGRAPHIC_PLANNING_FROM_INFOGRAPHIC_PLAN_EXECUTION,
        "infographic_planning_from_infographic_plan_observation": INFOGRAPHIC_PLANNING_FROM_INFOGRAPHIC_PLAN_OBSERVATION,
    }

@st_cache("Loading bootsrap code for sandbox environment at 'analytical_plan_execution' node", "data")
def load_analytical_sandbox_bootstrap() -> Dict[Literal["descriptive", "diagnostic", "predictive", "inferential"], str]:
    """
    Load sandbox bootstrap code.

    This function provides a dictionary of initialization code for the
    sandboxed execution environment categorized based on analysis type.
    """
    ignore_warnings: str = "import warnings\n"
    ignore_warnings += "warnings.filterwarnings('ignore')\n"
    pandas: str = "import pandas as pd\n"
    numpy: str =  "import numpy as np\n"
    scipy: str = "import scipy\n"
    sklearn: str = "import sklearn\n"
    df_load: str = "df = pd.read_csv('dataset.csv')\n"
    df_load += '\n' + "for column in df.columns:"
    df_load += '\n\t' + "if pd.api.types.is_object_dtype(df[column]):"
    df_load += '\n\t\t' + "try:"
    df_load += '\n\t\t\t' + "df[column] = pd.to_datetime(df[column])"
    df_load += '\n\t\t' + "except Exception as _:"
    df_load += '\n\t\t\t' + "pass\n"

    descriptive: str = ignore_warnings + pandas + numpy + df_load
    diagnostic: str = ignore_warnings + pandas + numpy + scipy + df_load
    predictive: str = ignore_warnings + pandas + numpy + scipy + df_load
    inferential: str = ignore_warnings + pandas + numpy + sklearn + df_load

    return {
        "descriptive": descriptive,
        "diagnostic": diagnostic,
        "predictive": predictive,
        "inferential": inferential,
    }

@st_cache("Loading bootsrap code for sandbox environment at 'infographic_plan_execution' node", "data")
def load_infographic_sandbox_bootstrap() -> str:
    """
    Load sandbox bootstrap code.

    This function provides initialization code for the sandboxed execution environment 
    to create an infographic in order to better communicate the analytical results.
    """
    ignore_warnings: str = "import warnings\n"
    ignore_warnings += "warnings.filterwarnings('ignore')\n"
    pandas: str = "import pandas as pd\n"
    numpy: str =  "import numpy as np\n"
    matplotlib: str = "import matplotlib.pyplot as plt\n"
    seaborn: str = "import seaborn as sns\n"
    df_load: str = "df = pd.read_csv('dataset.csv')\n"
    df_load += '\n' + "for column in df.columns:"
    df_load += '\n\t' + "if pd.api.types.is_object_dtype(df[column]):"
    df_load += '\n\t\t' + "try:"
    df_load += '\n\t\t\t' + "df[column] = pd.to_datetime(df[column])"
    df_load += '\n\t\t' + "except Exception as _:"
    df_load += '\n\t\t\t' + "pass\n"

    return ignore_warnings + pandas + numpy + matplotlib + seaborn + df_load
