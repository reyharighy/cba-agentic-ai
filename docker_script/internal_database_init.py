# pyright: reportUnknownMemberType=false

# third-party
from sqlalchemy import (
    Engine,
    create_engine,
)

# internal
from memory.database import internal_db_url
from memory.models.tables import metadata


def main() -> None:
    """
    Initialize internal database.
    """
    engine: Engine = create_engine(internal_db_url)

    metadata.create_all(
        bind=engine,
        checkfirst=True,
    )


if __name__ == "__main__":
    main()
