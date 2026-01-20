"""
Determine whether the user interface uses interactive graph mode
when agent processing request.

This feature is intended for testing purpose in a way that kind
give information which node is running when graph invoked.
"""
# standard
import os
from pathlib import Path

if os.getenv("ENABLE_INTERACTIVE_GRAPH", "false").lower() == "true":
    enable_interactive_graph: bool = True
else:
    enable_interactive_graph: bool = False

_BASE_DIR = Path(__file__).resolve().parent

images_source_path: str = str(_BASE_DIR)

__all__ = [
    "enable_interactive_graph",
    "images_source_path",
]
