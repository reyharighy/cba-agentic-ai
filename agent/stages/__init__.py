"""
Docstring for graph.stages
"""
# standard
import os

if os.getenv("ENABLE_INTERACTIVE_GRAPH", "false").lower() == "true":
    enable_interactive_graph: bool = True
else:
    enable_interactive_graph: bool = False

__all__ = [
    "enable_interactive_graph"
]
