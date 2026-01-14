"""
Docstring for context.context_manager
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
from pandas.errors import EmptyDataError
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
from .chat_history import (
    ChatHistory,
    ChatHistoryShow,
)
from .db_config import (
    external_db_url,
    internal_db_url,
)
from .db_table import (
    chat_histories,
    metadata,
    short_memories,
)
from .short_memory import (
    ShortMemory,
    ShortMemoryShow,
)

class DatabaseManager:
    """
    Docstring for ContextManager
    
    :var Returns: Description
    """
    def __init__(self) -> None:
        """
        Docstring for __init__
        
        :param self: Description
        """
        self.internal: Engine = create_engine(internal_db_url)
        self.external: Engine = create_engine(external_db_url)

    def init_internal_database(self) -> None:
        """
        Docstring for init_chat_history_db
        
        :param self: Description
        """
        metadata.create_all(self.internal)

    def index_chat_history(self) -> List[ChatHistory]:
        """
        Docstring for index_chat_history
        
        :param self: Description
        :return: Description
        :rtype: List[ChatHistory]
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
        Docstring for store_chat_history
        
        :param self: Description
        :param params: Description
        :type params: ChatHistory
        """
        with self.internal.begin() as connection:
            connection.execute(chat_histories.insert().values(**params.model_dump()))

    def show_chat_history(self, params: ChatHistoryShow) -> List[ChatHistory]:
        """
        Docstring for show_chat_history
        
        :param self: Description
        :param params: Description
        :type params: ChatHistoryShow
        :return: Description
        :rtype: List[ChatHistory]
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
        Docstring for index_short_memory
        
        :param self: Description
        :return: Description
        :rtype: List[ShortMemory]
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
        Docstring for store_short_memory
        
        :param self: Description
        :param params: Description
        :type params: ShortMemory
        """
        with self.internal.begin() as connection:
            connection.execute(short_memories.insert().values(**params.model_dump()))

    def show_short_memory(self, params: ShortMemoryShow) -> Optional[ShortMemory]:
        """
        Docstring for store_short_memory
        
        :param self: Description
        :param params: Description
        :type params: ShortMemoryShow
        :return: Description
        :rtype: Optional[ShortMemory]
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
        Docstring for inspect_external_database
        
        :param self: Description
        :return: Description
        :rtype: Dict[str, List[Any] | Dict[Any, Any]]
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

    def get_working_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Docstring for get_working_dataframe
        
        :param self: Description
        :return: Description
        :rtype: DataFrame | None
        """
        try:
            return pd.read_csv("./context/working_dataset.csv")
        except EmptyDataError as _:
            return None

    def get_last_executed_sql_query(self) -> Optional[str]:
        """
        Docstring for get_last_executed_sql_query
        
        :param self: Description
        :return: Description
        :rtype: str | None
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

    def retrieve_external_data(self, statement: str) -> None:
        """
        Docstring for retrieve_external_data
        
        :param self: Description
        :param statement: Description
        :type statement: str
        """
        output_path: Path = Path("./context/working_dataset.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.external.begin() as connection:
            df = pd.read_sql(text(statement), connection)
            df.to_csv(output_path, index=False, encoding="utf-8")
