"""
Path configuration for working datasets.

This module provides a reference to the location where
datasets used during application execution are stored.
"""
import os

working_dataset_path: str = os.getenv("WORKING_DATASET_FILE", "")

__all__ = [
    "working_dataset_path"
]