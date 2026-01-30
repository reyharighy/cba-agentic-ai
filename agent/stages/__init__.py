# standard
import os
from pathlib import Path

if os.getenv("ENABLE_INTERACTIVE_GRAPH", "false").lower() == "true":
    enable_interactive_graph: bool = True
else:
    enable_interactive_graph: bool = False

images_source_path: str = str(Path(__file__).resolve().parent)

__all__ = [
    "enable_interactive_graph",
    "images_source_path",
]
