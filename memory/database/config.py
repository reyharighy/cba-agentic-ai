"""
Database configuration module for internal system.

This module is responsible for resolving database connection settings
from the execution environment and exposing database URLs required
by the application.
"""
# standard
import os
from typing import Optional

sqlite_db_path: Optional[str] = os.getenv("SQLITE_DB_PATH", None)

if sqlite_db_path is None:
    raise ValueError("'SQLITE_DB_PATH' is not found in config file.")

internal_db_url: str = f"sqlite:///{sqlite_db_path}/context.db"
