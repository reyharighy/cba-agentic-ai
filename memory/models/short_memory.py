"""
Short-term memory data models.

This module defines representations of condensed contextual
information derived from conversational interactions.
"""
# standard
from datetime import datetime
from typing import Optional

# third-party
from pydantic import (
    BaseModel,
    Field,
)

class ShortMemory(BaseModel):
    """
    Representation of a short-term contextual memory entry.

    This model stores summarized information associated
    with a specific point in a conversation.
    """
    turn_num: int = Field(ge=1)
    summary: str = Field(min_length=1)
    sql_query: Optional[str] = Field(min_length=1, default=None)
    created_at: datetime = Field(default_factory=datetime.now)

class ShortMemoryCreate(BaseModel):
    """
    Input model for creating short memory entries.

    This model represents the data required to construct
    a short-term memory record.
    """
    turn_num: int
    summary: str
    sql_query: Optional[str]

    def __call__(self) -> ShortMemory:
        """
        Create a short memory instance from the input data.

        This method converts the creation model into
        its corresponding persisted representation.
        """
        return ShortMemory(
            turn_num=self.turn_num,
            summary=self.summary,
            sql_query=self.sql_query
        )

class ShortMemoryShow(BaseModel):
    """
    Minimal view model for short memory lookup.

    This model represents the identifier used to
    reference or retrieve a short-term memory entry.
    """
    turn_num: int
