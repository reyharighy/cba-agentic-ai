"""
Path configuration for working datasets.

This module provides a reference to the location where
datasets used during application execution are stored.
"""
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent

working_dataset_path: str = str(_BASE_DIR / "dataset.csv")

__all__ = [
    "working_dataset_path"
]
