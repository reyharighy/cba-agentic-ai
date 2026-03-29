# pyright: reportUnknownMemberType=false

# standard
from collections.abc import Sequence
from typing import Any

# third-party
import pandas as pd
from sqlalchemy import (
    Engine,
    DATE,
    DATETIME,
    INTEGER,
    Row,
    TextClause,
    TIMESTAMP,
    NUMERIC,
    UUID,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.exc import ProgrammingError

# internal
from context.datasets import dataset_file_path


class ContextManager:
    def __init__(self, external_db_url: str) -> None:
        """
        Initialize ContextManager.
        """
        self.external: Engine = create_engine(external_db_url)

    def inspect_external_database(self) -> dict[str, list[dict[str, Any]]]:
        """
        Inspect external database and return table names and column details.
        """
        inspector: Any = inspect(self.external)
        table_names: list[str] = inspector.get_table_names()
        table_columns: dict[str, list[dict[str, Any]]] = {}

        with self.external.begin() as connection:
            for table_name in table_names:
                # Tables of "chat_histories" and "short_memories" are part of internal database.
                # As we use the same instance of PostgreSQL for both internal and external databases, we need to skip these tables during inspection.
                # In reality, these tables won't exist in external database.
                # Mind to remove this condition if using separate instances for internal and external databases.
                if table_name in ["chat_histories", "short_memories"]:
                    continue

                columns: list[dict[str, Any]] = inspector.get_columns(table_name)
                table_columns[table_name] = []

                for column in columns:
                    if (
                        not isinstance(
                            column["type"],
                            TIMESTAMP,
                        )
                        and not isinstance(
                            column["type"],
                            DATETIME,
                        )
                        and not isinstance(column["type"], DATE)
                    ):
                        limit_stmt: str = (
                            "LIMIT 1"
                            if isinstance(column["type"], UUID)
                            else "LIMIT 2"
                            if isinstance(column["type"], NUMERIC) or isinstance(column["type"], INTEGER)
                            else ""
                        )

                        sql_query: TextClause = text(f"""
                            SELECT DISTINCT {column["name"]}
                            FROM {table_name}
                            WHERE {column["name"]} IS NOT NULL
                            {limit_stmt};
                        """)

                        result: Sequence[Row[Any]] = connection.execute(sql_query).fetchall()

                        table_columns[table_name].append(
                            {
                                "name": column["name"],
                                "type": column["type"],
                                "comment": column["comment"],
                                "sample_values": [row[0] for row in result],
                            }
                        )
                    else:
                        get_earliest_time_sql_query: TextClause = text(f"""
                            SELECT DISTINCT {column["name"]}
                            FROM {table_name}
                            WHERE {column["name"]} IS NOT NULL
                            ORDER BY {column["name"]} ASC
                            LIMIT 1;
                        """)

                        get_latest_time_sql_query: TextClause = text(f"""
                            SELECT DISTINCT {column["name"]}
                            FROM {table_name}
                            WHERE {column["name"]} IS NOT NULL
                            ORDER BY {column["name"]} DESC
                            LIMIT 1;
                        """)

                        earliest: Row[Any] | None = connection.execute(get_earliest_time_sql_query).first()
                        latest: Row[Any] | None = connection.execute(get_latest_time_sql_query).first()

                        table_columns[table_name].append(
                            {
                                "name": column["name"],
                                "type": column["type"],
                                "comment": column["comment"],
                                "earliest_timestamp": earliest,
                                "latest_timestamp": latest,
                            }
                        )

        return table_columns

    def extract_external_database(self, statement: str) -> ValueError | None:
        """
        Extract data from external database based on the provided SQL statement and save it to a CSV file.
        """
        try:
            with self.external.begin() as connection:
                df: pd.DataFrame = pd.read_sql(text(statement), connection)
                df.to_csv(
                    dataset_file_path,
                    index=False,
                    encoding="utf-8",
                )
        except ProgrammingError as e:
            return ValueError(str(e.orig))
