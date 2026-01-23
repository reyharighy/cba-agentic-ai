"""
Cache utilities for application context.

This module provides cached access to context-related resources
used across different parts of the application.
"""
# standard
from typing import Dict

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
    }
