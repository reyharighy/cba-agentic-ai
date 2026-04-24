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
    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.now,
    ),
)

short_memories = Table(
    "short_memories",
    metadata,
    Column("turn_num", Integer, nullable=False),
    Column("summary", String, nullable=False),
    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.now,
    ),
)

state_transitions = Table(
    "state_transitions",
    metadata,
    Column("thread_id", String, nullable=False, index=True),
    Column("turn_num", Integer, nullable=False, index=True),
    Column("sequence_num", Integer, nullable=False),
    Column("node_name", String, nullable=False),
    Column("event_type", String, nullable=False),
    Column("payload_digest", String, nullable=True),
    Column("payload_size", Integer, nullable=True),
    Column("payload_preview", String, nullable=True),
    Column("error_message", String, nullable=True),
    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.now,
    ),
)
