"""
Docstring for graph.runtime
"""
# standard
from dataclasses import dataclass
from typing import Dict

@dataclass
class Context:
    """
    Docstring for Context
    """
    turn_num: int
    prompts_set: Dict[str, str]
    sandbox_bootstrap: str
