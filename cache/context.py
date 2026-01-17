"""
Cache utilities for application context.

This module provides cached access to context-related resources
used across different parts of the application.
"""
# internal
from context.database import (
    DatabaseManager,
    internal_db_url,
    external_db_url,
)
from util import st_cache

@st_cache("Loading database manager", "resource")
def load_database_manager() -> DatabaseManager:
    """
    Load the database manager instance.

    This function provides access to the database manager used by
    the application.
    """
    return DatabaseManager(
        internal_db_url=internal_db_url,
        external_db_url=external_db_url
    )
