"""
Docstring for graph.runtime
"""
# standard
from dataclasses import dataclass
from typing import (
    Dict,
    List,
    Union,
)

# internal
from context import ShortMemory

@dataclass
class Context:
    """
    Docstring for Context
    """
    turn_num: int
    prompts_set: Dict[str, str]
    short_memories: List[ShortMemory]
    external_db_info: Dict[str, Union[List, Dict]]
    sandbox_bootstrap: str
