"""
Docstring for application.runtime
"""
# standard
from dataclasses import dataclass
from typing import Optional

@dataclass
class SessionMemory:
    """
    Docstring for SessionMemory
    """
    turn_num: int = 0
    chat_input: Optional[str] = None
    chat_output: Optional[str] = None
    thinking: Optional[str] = None
