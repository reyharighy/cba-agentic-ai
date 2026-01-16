"""
Docstring for context.datasets
"""
import os

working_dataset_path: str = os.getenv("WORKING_DATASET_FILE", "")

__all__ = [
    "working_dataset_path"
]