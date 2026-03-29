# standard
import os

postgres_port: str | None = os.getenv("POSTGRES_PORT", None)

if postgres_port is None:
    raise ValueError("'POSTGRES_PORT' is not found in config file.")

postgres_user: str | None = os.getenv("POSTGRES_USER", None)

if postgres_user is None:
    raise ValueError("'POSTGRES_USER' is not found in config file.")

postgres_password: str | None = os.getenv("POSTGRES_PASSWORD", None)

if postgres_password is None:
    raise ValueError("'POSTGRES_PASSWORD' is not found in config file.")

postgres_db: str | None = os.getenv("POSTGRES_DB", None)

if postgres_db is None:
    raise ValueError("'POSTGRES_DB' is not found in config file.")

internal_db_url: str = f"postgresql+psycopg2://{postgres_user}:{postgres_password}@pgsql:{postgres_port}/{postgres_db}"

__all__ = ["internal_db_url"]
