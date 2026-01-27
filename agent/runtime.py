"""
Runtime-level context definitions for graph execution.

This module defines immutable contextual data that is injected into
graph execution at runtime. The context provides shared, read-only
information required by multiple nodes during a single execution cycle
"""
# standard
from dataclasses import dataclass
from typing import (
    Dict,
    Literal
)

@dataclass
class Context:
    """
    Execution context shared across all graph nodes.

    This class represents runtime-scoped information that does not belong
    to the evolving graph state. It is intended to carry execution metadata
    and static resources needed by nodes while the graph is running.
    """
    turn_num: int
    prompts_set: Dict[str, str]
    analytical_sandbox_bootstrap: Dict[Literal["descriptive", "diagnostic", "predictive", "inferential"], str]
    infographic_sandbox_bootstrap: str
