# standard
import os

# third-party
from dotenv import load_dotenv

load_dotenv()

agent_postgres_host: str | None = os.getenv("AGENT_POSTGRES_HOST", None)

if agent_postgres_host is None:
    raise ValueError("'AGENT_POSTGRES_HOST' is not found in config file.")

agent_postgres_port: str | None = os.getenv("AGENT_POSTGRES_PORT", None)

if agent_postgres_port is None:
    raise ValueError("'AGENT_POSTGRES_PORT' is not found in config file.")

agent_postgres_user: str | None = os.getenv("AGENT_POSTGRES_USER", None)

if agent_postgres_user is None:
    raise ValueError("'AGENT_POSTGRES_USER' is not found in config file.")

agent_postgres_password: str | None = os.getenv("AGENT_POSTGRES_PASSWORD", None)

if agent_postgres_password is None:
    raise ValueError("'AGENT_POSTGRES_PASSWORD' is not found in config file.")

agent_postgres_db: str | None = os.getenv("AGENT_POSTGRES_DB", None)

if agent_postgres_db is None:
    raise ValueError("'AGENT_POSTGRES_DB' is not found in config file.")

internal_db_url: str = (
    f"postgresql+psycopg2://{agent_postgres_user}:{agent_postgres_password}"
    f"@{agent_postgres_host}:{agent_postgres_port}/{agent_postgres_db}"
)

__all__ = [
    "internal_db_url",
]
