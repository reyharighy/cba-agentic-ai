"""
Cache utilities for application context.

This module provides cached access to context-related resources
used across different parts of the application.
"""
# internal
from context.database import (
    ContextManager,
    external_db_url,
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
