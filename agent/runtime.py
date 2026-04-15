# standard
import os
from dataclasses import dataclass
from typing import Literal


def read_enable_infographic_from_env() -> bool:
    """
    When false (default), the graph skips the infographic subgraph entirely
    (no assessment node, no chart-generation branch).
    """
    return os.environ.get("ENABLE_INFOGRAPHIC", "false").lower() in ("true", "1", "yes")


@dataclass
class Context:
    """
    Runtime context for the analytical and infographic generation process.
    """

    turn_num: int
    prompts_set: dict[str, str]
    analytical_sandbox_bootstrap: dict[Literal["descriptive", "diagnostic", "predictive", "inferential"], str]
    infographic_sandbox_bootstrap: str
    enable_infographic: bool
