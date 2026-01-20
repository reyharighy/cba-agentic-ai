"""
Database configuration module for external system.

This module is responsible for resolving database connection settings
from the execution environment and exposing database URLs required
by the application.
"""
# standard
import os
from typing import Optional

# third-party
from dotenv import load_dotenv

load_dotenv()

postgres_port: Optional[str] = os.getenv("POSTGRES_PORT", None)

if postgres_port is None:
    raise ValueError("'POSTGRES_PORT' is not found in config file.")

postgres_user: Optional[str] = os.getenv("POSTGRES_USER", None)

if postgres_user is None:
    raise ValueError("'POSTGRES_USER' is not found in config file.")

postgres_password: Optional[str] = os.getenv("POSTGRES_PASSWORD", None)

if postgres_password is None:
    raise ValueError("'POSTGRES_PASSWORD' is not found in config file.")

postgres_db: Optional[str] = os.getenv("POSTGRES_DB", None)

if postgres_db is None:
    raise ValueError("'POSTGRES_DB' is not found in config file.")

external_db_url: str = f"postgresql+psycopg2://{postgres_user}:{postgres_password}@pgsql:{postgres_port}/{postgres_db}"
