"""
Cache utilities for application memory.

This module provides cached access to memory-related resources
used by the agent to enhance interaction.
"""
from memory.database import (
    MemoryManager,
    internal_db_url,
)
from util import st_cache

@st_cache("Loading database manager", "resource")
def load_memory_manager() -> MemoryManager:
    """
    Load the context manager instance.

    This function provides access to the internal storage used by
    agent to have a capability to memorize interaction.
    """
    return MemoryManager(internal_db_url)
