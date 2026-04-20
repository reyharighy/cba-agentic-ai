# standard
import os

# third-party
from dotenv import load_dotenv

load_dotenv()

business_postgres_host: str | None = os.getenv("BUSINESS_POSTGRES_HOST", None)

if business_postgres_host is None:
    raise ValueError("'BUSINESS_POSTGRES_HOST' is not found in config file.")

business_postgres_port: str | None = os.getenv("BUSINESS_POSTGRES_PORT", None)

if business_postgres_port is None:
    raise ValueError("'BUSINESS_POSTGRES_PORT' is not found in config file.")

business_postgres_user: str | None = os.getenv("BUSINESS_POSTGRES_USER", None)

if business_postgres_user is None:
    raise ValueError("'BUSINESS_POSTGRES_USER' is not found in config file.")

business_postgres_password: str | None = os.getenv("BUSINESS_POSTGRES_PASSWORD", None)

if business_postgres_password is None:
    raise ValueError("'BUSINESS_POSTGRES_PASSWORD' is not found in config file.")

business_postgres_db: str | None = os.getenv("BUSINESS_POSTGRES_DB", None)

if business_postgres_db is None:
    raise ValueError("'BUSINESS_POSTGRES_DB' is not found in config file.")

external_db_url: str = (
    f"postgresql+psycopg2://{business_postgres_user}:{business_postgres_password}"
    f"@{business_postgres_host}:{business_postgres_port}/{business_postgres_db}"
)

__all__ = [
    "external_db_url",
]
