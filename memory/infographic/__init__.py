"""
Path configuration for working datasets.

This module provides a reference to the location where
datasets used during application execution are stored.
"""
from pathlib import Path

infographic_path: Path = Path(__file__).resolve().parent

__all__ = [
    "infographic_path"
]
