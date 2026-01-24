"""
Database management abstraction.

This module defines a unified interface for interacting with
external data sources used by the application.
"""
# internal
from typing import (
    Any,
    Dict,
    Literal,
    List,
    Sequence,
    Optional,
    Union,
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
from context.datasets import working_dataset_path

class ContextManager:
    def __init__(self, external_db_url: str) -> None:
        """
        Initialize database connections.

        This constructor prepares database engines for external data access
        based on the provided connection URLs.
        """
        self.external: Engine = create_engine(external_db_url)

    def inspect_external_database(self) -> Dict[Literal["tables", "columns"], Union[List, Dict]]:
        """
        Inspect the structure of the external database.

        This method gathers structural information about external data sources
        to support downstream analysis and reasoning.
        """
        inspector: Any = inspect(self.external)
        table_names: List[str] = inspector.get_table_names()
        table_columns: Dict[str, List[Dict[str, Any]]] = {}

        with self.external.begin() as connection:
            for table_name in table_names:
                columns: List[Dict[str, Any]] = inspector.get_columns(table_name)
                table_columns[table_name] = []

                for column in columns:
                    if not isinstance(column["type"], TIMESTAMP) and not isinstance(column["type"], DATETIME) and not isinstance(column["type"], DATE):
                        sql_query: TextClause = text(f"""
                            SELECT DISTINCT {column["name"]}
                            FROM {table_name}
                            WHERE {column["name"]} IS NOT NULL
                            {"LIMIT 3" if not isinstance(column["type"], VARCHAR) else ""};
                        """)

                        result: Sequence[Row] = connection.execute(sql_query).fetchall()

                        table_columns[table_name].append({
                            "name": column["name"],
                            "type": column["type"],
                            "comment": column["comment"],
                            "sample_values": [row[0] for row in result],
                        })
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

                        earliest: Optional[Row[Any]] = connection.execute(get_earliest_time_sql_query).first()
                        latest: Optional[Row[Any]] = connection.execute(get_latest_time_sql_query).first()

                        table_columns[table_name].append({
                            "name": column["name"],
                            "type": column["type"],
                            "comment": column["comment"],
                            "earliest": earliest,
                            "latest": latest
                        })

        return {
            "tables": table_names,
            "columns": table_columns
        }

    def extract_external_database(self, statement: str) -> Optional[ValueError]:
        """
        Extract data from the external database.

        This method executes a query against an external data source and
        materializes the result into a dataset usable by the system.
        """
        try:
            with self.external.begin() as connection:
                df = pd.read_sql(text(statement), connection)
                df.to_csv(working_dataset_path, index=False, encoding="utf-8")
        except ProgrammingError as e:
            return ValueError(str(e.orig))
