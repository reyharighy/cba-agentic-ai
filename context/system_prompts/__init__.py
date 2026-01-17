"""
System prompt registry.

This package centralizes all system-level prompts used during
graph execution, providing a dedicated and inspectable location
for prompt definitions across different orchestration nodes.
"""
from .prompts import (
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

__all__ = [
    "ANALYSIS_RESPONSE",
    "ANALYSIS_ORCHESTRATION",
    "COMPUTATION_PLANNING",
    "DATA_UNAVAILABILITY",
    "DIRECT_RESPONSE",
    "INTENT_COMPREHENSION",
    "OBSERVATION",
    "PUNT_RESPONSE",
    "REQUEST_CLASSIFICATION",
    "SELF_CORRECTION",
    "SELF_REFLECTION",
    "SUMMARIZATION",
]