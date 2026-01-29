"""
Cache utilities for application memory.

This module provides cached access to memory-related resources
used by the agent to enhance interaction.
"""
# standard
from importlib.abc import Loader
from importlib.util import (
    module_from_spec,
    spec_from_file_location,
)
from pathlib import Path
from types import ModuleType
from typing import (
    Optional,
    Tuple
)

# internal
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

@st_cache("Loading infographic object", "resource")
def load_infographic(infographic_object_file_path: Path) -> Tuple[Optional[Loader], Optional[ModuleType]]:
    """Load the module of the manifest file to be executed.

    The result is cached using the default Streamlit st.cache_resource decorator.

    Args:
        manifest_dir: Directory of manifest file is located.
        manifest_file: Name of the manifest file including its extension.

    Returns:
        A tuple Loader and ModuleType if both exist.

    """
    spec = spec_from_file_location(
        name=infographic_object_file_path.stem,
        location=infographic_object_file_path
    )

    return (spec.loader, module_from_spec(spec)) if spec else (None, None)
