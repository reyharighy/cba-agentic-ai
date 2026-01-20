"""
Database management abstraction.

This module defines a unified interface for interacting with both
internal system storage used by the application.
"""
# internal
from typing import (
    List,
    Optional,
)

# third-party
from sqlalchemy import (
    CursorResult,
    Engine,
    create_engine,
    select,
)

# internal
from memory.models import (
    ChatHistory,
    ChatHistoryShow,
    ShortMemory,
    ShortMemoryShow,
    chat_histories,
    short_memories,
    table_schema_metadata,
)

class MemoryManager:
    def __init__(self, internal_db_url: str) -> None:
        """
        Initialize database connections.

        This constructor prepares database engines for internal system storage
        based on the provided connection URLs.
        """
        self.internal: Engine = create_engine(internal_db_url)

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
