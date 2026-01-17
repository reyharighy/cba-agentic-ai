"""
Database management abstraction.

This module defines a unified interface for interacting with both
internal system storage and external data sources used by the application.
"""
# internal
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Sequence,
    Optional,
    Union,
)

# third-party
import pandas as pd
from sqlalchemy import (
    CursorResult,
    Engine,
    DATE,
    DATETIME,
    Row,
    TextClause,
    TIMESTAMP,
    VARCHAR,
    create_engine,
    inspect,
    select,
    text,
)

# internal
from context.datasets import working_dataset_path
from context.models import (
    ChatHistory,
    ChatHistoryShow,
    ShortMemory,
    ShortMemoryShow,
    chat_histories,
    short_memories,
    table_schema_metadata,
)

class DatabaseManager:
    def __init__(self, internal_db_url: str, external_db_url: str) -> None:
        """
        Initialize database connections.

        This constructor prepares database engines for internal system storage
        and external data access based on the provided connection URLs.
        """
        self.internal: Engine = create_engine(internal_db_url)
        self.external: Engine = create_engine(external_db_url)

    def init_internal_database(self) -> None:
        """
        Initialize internal database schema.

        This method ensures that required internal tables are available
        for system operation.
        """
        table_schema_metadata.create_all(self.internal)

    def index_chat_history(self) -> List[ChatHistory]:
        """
        Retrieve all stored chat history entries.

        This method returns the full set of recorded conversational history
        maintained by the system.
        """
        with self.internal.begin() as connection:
            result: CursorResult = connection.execute(
                select(chat_histories).order_by(
                    chat_histories.c.turn_num,
                    chat_histories.c.created_at
                )
            )

            return [ChatHistory.model_validate(row) for row in result.mappings()]

    def store_chat_history(self, params: ChatHistory) -> None:
        """
        Persist a chat history entry.

        This method records a conversational interaction into internal storage.
        """
        with self.internal.begin() as connection:
            connection.execute(chat_histories.insert().values(**params.model_dump()))

    def show_chat_history(self, params: ChatHistoryShow) -> List[ChatHistory]:
        """
        Retrieve chat history for a specific interaction context.

        This method returns chat history entries associated with a given scope.
        """
        with self.internal.begin() as connection:
            result: CursorResult = connection.execute(
                select(chat_histories).where(
                    chat_histories.c.turn_num == params.turn_num
                ).order_by(
                    chat_histories.c.created_at
                )
            )

            return [ChatHistory.model_validate(row) for row in result.mappings()]

    def index_short_memory(self) -> List[ShortMemory]:
        """
         Retrieve all short-term memory entries.

        This method returns the collection of short-term memory records
        maintained by the system.
        """
        with self.internal.begin() as connection:
            result: CursorResult = connection.execute(
                select(short_memories).order_by(
                    short_memories.c.turn_num,
                    short_memories.c.created_at
                )
            )

            return [ShortMemory.model_validate(row) for row in result.mappings()]

    def store_short_memory(self, params: ShortMemory) -> None:
        """
        Persist a short-term memory entry.

        This method records temporary system memory into internal storage.
        """
        with self.internal.begin() as connection:
            connection.execute(short_memories.insert().values(**params.model_dump()))

    def show_short_memory(self, params: ShortMemoryShow) -> Optional[ShortMemory]:
        """
        Retrieve short-term memory for a specific context.

        This method returns the most relevant short-term memory entry
        for the given scope, if available.
        """
        with self.internal.begin() as connection:
            result: CursorResult = connection.execute(
                select(short_memories).where(
                    short_memories.c.turn_num == params.turn_num
                ).order_by(
                    short_memories.c.created_at
                )
            )

            mappings: List[ShortMemory] = [ShortMemory.model_validate(row) for row in result.mappings()]

            return mappings.pop() if mappings else None

    def inspect_external_database(self) -> Dict[str, Union[List, Dict]]:
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

    def show_last_saved_sql_query(self) -> Optional[str]:
        """
        Retrieve the most recent stored query.

        This method returns the last query recorded by the system, if present.
        """
        with self.internal.begin() as connection:
            result: CursorResult = connection.execute(
                select(short_memories).where(
                    short_memories.c.sql_query.isnot(None)
                ).order_by(
                    short_memories.c.created_at.desc()
                ).limit(1)
            )

            mappings: List[ShortMemory] = [ShortMemory.model_validate(row) for row in result.mappings()]

            return mappings.pop().sql_query if mappings else None

    def extract_external_database(self, statement: str) -> None:
        """
        Extract data from the external database.

        This method executes a query against an external data source and
        materializes the result into a dataset usable by the system.
        """
        output_path: Path = Path(working_dataset_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.external.begin() as connection:
            df = pd.read_sql(text(statement), connection)
            df.to_csv(output_path, index=False, encoding="utf-8")
