# standard
from dataclasses import dataclass
from typing import Literal


@dataclass
class Context:
    """
    Runtime context for the analytical execution process.
    """

    turn_num: int
    prompts_set: dict[str, str]
    analytical_sandbox_bootstrap: dict[Literal["descriptive", "diagnostic", "predictive", "inferential"], str]
