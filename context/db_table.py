"""
Docstring for context.table
"""
# standard
from datetime import datetime

# third-party
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
)

metadata = MetaData()

chat_histories = Table(
    "chat_histories",
    metadata,
    Column("turn_num", Integer, nullable=False),
    Column("role", String, nullable=False),
    Column("content", String, nullable=False),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
)

short_memories = Table(
    "short_memories",
    metadata,
    Column("turn_num", Integer, nullable=False),
    Column("summary", String, nullable=False),
    Column("sql_query", String, nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.now),
)
