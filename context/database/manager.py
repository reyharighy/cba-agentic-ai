# pyright: reportUnknownMemberType=false

# standard
from collections.abc import Sequence
from typing import (
    Any,
    Literal,
)

# third-party
import pandas as pd
from sqlalchemy import (
    Engine,
    DATE,
    DATETIME,
    Row,
    TextClause,
    TIMESTAMP,
    VARCHAR,
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

    def inspect_external_database(
        self,
    ) -> dict[
        Literal["tables", "columns"],
        list[str] | dict[str, Any],
    ]:
        """
        Inspect external database and return table names and column details.
        """
        inspector: Any = inspect(self.external)
        table_names: list[str] = inspector.get_table_names()
        table_columns: dict[str, list[dict[str, Any]]] = {}

        with self.external.begin() as connection:
            for table_name in table_names:
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
                        sql_query: TextClause = text(f"""
                            SELECT DISTINCT {column["name"]}
                            FROM {table_name}
                            WHERE {column["name"]} IS NOT NULL
                            {"LIMIT 3" if not isinstance(column["type"], VARCHAR) else ""};
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
                                "earliest": earliest,
                                "latest": latest,
                            }
                        )

        return {
            "tables": table_names,
            "columns": table_columns,
        }

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
