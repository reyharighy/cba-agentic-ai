"""
Determine whether the user interface uses interactive graph mode
when agent processing request.

This feature is intended for testing purpose in a way that kind
give information which node is running when graph invoked.
"""
# standard
import os
from pathlib import Path

enable_interactive_graph: bool = True if os.getenv("ENABLE_INTERACTIVE_GRAPH", "false").lower() == "true" else False
images_source_path: str = str(Path(__file__).resolve().parent)

__all__ = [
    "enable_interactive_graph",
    "images_source_path",
]
