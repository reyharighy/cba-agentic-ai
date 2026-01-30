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
    table_schema_metadata,
)


class MemoryManager:
    def __init__(self, internal_db_url: str) -> None:
        """
        Docstring for __init__

        :param self: Description
        :param internal_db_url: Description
        :type internal_db_url: str
        """
        self.internal: Engine = create_engine(internal_db_url)

    def init_internal_database(self) -> None:
        """
        Docstring for init_internal_database

        :param self: Description
        """
        table_schema_metadata.create_all(self.internal)

    def index_chat_history(self) -> list[ChatHistory]:
        """
        Docstring for index_chat_history

        :param self: Description
        :return: Description
        :rtype: list[ChatHistory]
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
        Docstring for store_chat_history

        :param self: Description
        :param params: Description
        :type params: ChatHistory
        """
        with self.internal.begin() as connection:
            connection.execute(chat_histories.insert().values(**params.model_dump()))

    def show_chat_history(self, params: ChatHistoryShow) -> list[ChatHistory]:
        """
        Docstring for show_chat_history

        :param self: Description
        :param params: Description
        :type params: ChatHistoryShow
        :return: Description
        :rtype: list[ChatHistory]
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
        Docstring for index_short_memory

        :param self: Description
        :return: Description
        :rtype: list[ShortMemory]
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
        Docstring for store_short_memory

        :param self: Description
        :param params: Description
        :type params: ShortMemory
        """
        with self.internal.begin() as connection:
            connection.execute(short_memories.insert().values(**params.model_dump()))

    def show_short_memory(self, params: ShortMemoryShow) -> ShortMemory | None:
        """
        Docstring for show_short_memory

        :param self: Description
        :param params: Description
        :type params: ShortMemoryShow
        :return: Description
        :rtype: ShortMemory | None
        """
        with self.internal.begin() as connection:
            result: CursorResult[Row[Any]] = connection.execute(
                select(short_memories)
                .where(short_memories.c.turn_num == params.turn_num)
                .order_by(short_memories.c.created_at)
            )

            mappings: list[ShortMemory] = [ShortMemory.model_validate(row) for row in result.mappings()]

            return mappings.pop() if mappings else None
