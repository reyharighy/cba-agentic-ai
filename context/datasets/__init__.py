"""
Path configuration for working datasets.

This module provides a reference to the location where
datasets used during application execution are stored.
"""
from pathlib import Path

working_dataset_path: Path = Path(__file__).resolve().parent / "dataset.csv"

__all__ = [
    "working_dataset_path"
]
