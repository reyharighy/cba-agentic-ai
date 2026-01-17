"""
Database context for the application.

This package defines the public interface for database-related concerns,
including database configuration and the database manager abstraction
used throughout the system.
"""
from .config import (
    internal_db_url,
    external_db_url,
)
from .manager import DatabaseManager

__all__ = [
    "internal_db_url",
    "external_db_url",
    "DatabaseManager",
]
