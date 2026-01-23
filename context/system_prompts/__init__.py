"""
System prompt registry.

This package centralizes all system-level prompts used during
graph execution, providing a dedicated and inspectable location
for prompt definitions across different orchestration nodes.
"""
from .prompts import (
    INTENT_COMPREHENSION,
    REQUEST_CLASSIFICATION,
    PUNT_RESPONSE,
    ANALYTICAL_REQUIREMENT,
)

__all__ = [
    "INTENT_COMPREHENSION",
    "PUNT_RESPONSE",
    "REQUEST_CLASSIFICATION",
    "ANALYTICAL_REQUIREMENT",
]