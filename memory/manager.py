# third-party
from typing import Any
from sqlalchemy import (
    CursorResult,
    Engine,
    Row,
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
)


class MemoryManager:
    def __init__(self, internal_db_url: str) -> None:
        """
        Initialize MemoryManager
        """
        self.internal: Engine = create_engine(internal_db_url)

    def index_chat_history(self) -> list[ChatHistory]:
        """
        Get all chat history records.
        """
        with self.internal.begin() as connection:
            result: CursorResult[Row[Any]] = connection.execute(
                select(chat_histories).order_by(
                    chat_histories.c.turn_num,
                    chat_histories.c.created_at,
                )
            )

            return [ChatHistory.model_validate(row) for row in result.mappings()]

    def store_chat_history(self, params: ChatHistory) -> None:
        """
        Store a chat history record.
        """
        with self.internal.begin() as connection:
            connection.execute(chat_histories.insert().values(**params.model_dump()))

    def show_chat_history(self, params: ChatHistoryShow) -> list[ChatHistory]:
        """
        Show chat history for a specific turn number.
        """
        with self.internal.begin() as connection:
            result: CursorResult[Row[Any]] = connection.execute(
                select(chat_histories)
                .where(chat_histories.c.turn_num == params.turn_num)
                .order_by(chat_histories.c.created_at)
            )

            return [ChatHistory.model_validate(row) for row in result.mappings()]

    def index_short_memory(self) -> list[ShortMemory]:
        """
        Get all short memory records.
        """
        with self.internal.begin() as connection:
            result: CursorResult[Row[Any]] = connection.execute(
                select(short_memories).order_by(
                    short_memories.c.turn_num,
                    short_memories.c.created_at,
                )
            )

            return [ShortMemory.model_validate(row) for row in result.mappings()]

    def store_short_memory(self, params: ShortMemory) -> None:
        """
        Store a short memory record.
        """
        with self.internal.begin() as connection:
            connection.execute(short_memories.insert().values(**params.model_dump()))

    def show_short_memory(self, params: ShortMemoryShow) -> ShortMemory | None:
        """
        Show the most recent short memory for a specific turn number.
        """
        with self.internal.begin() as connection:
            result: CursorResult[Row[Any]] = connection.execute(
                select(short_memories)
                .where(short_memories.c.turn_num == params.turn_num)
                .order_by(short_memories.c.created_at)
            )

            mappings: list[ShortMemory] = [ShortMemory.model_validate(row) for row in result.mappings()]

            return mappings.pop() if mappings else None
