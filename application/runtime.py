"""
Runtime state definitions for the application layer.

This module defines lightweight, in-memory data structures used to track
UI session state across a single user interaction flow.
"""
# standard
from dataclasses import dataclass
from typing import Optional

@dataclass
class SessionMemory:
    """
    Ephemeral UI session state.

    This structure stores transient data related to a single chat session,
    such as the current turn number, user input, streamed output, and
    intermediate reasoning text intended for display only.

    This state is not persisted and must not be treated as a source of truth.
    """
    turn_num: int = 0
    chat_input: Optional[str] = None
    chat_output: Optional[str] = None
    thinking: Optional[str] = None
