"""
Chat history data models.

This module defines representations of conversational turns
that are persisted as part of the system's interaction history.
"""
# standard
from datetime import datetime
from typing import Literal

# third-party
from pydantic import (
    BaseModel,
    Field
)

class ChatHistory(BaseModel):
    """
    Representation of a single conversational turn.

    This model captures one exchange within a conversation.
    """
    turn_num: int = Field(ge=1)
    role: Literal["Human", "AI"]
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)

class ChatHistoryCreate(BaseModel):
    """
    Input model for creating chat history records.

    This model represents the required information needed
    to construct a persisted chat history entry.
    """
    turn_num: int
    role: Literal["Human", "AI"]
    content: str

    def __call__(self) -> ChatHistory:
        """
        Create a chat history instance from the input data.

        This method converts the creation model into
        its corresponding persisted representation.
        """
        return ChatHistory(
            turn_num=self.turn_num,
            role=self.role,
            content=self.content
        )

class ChatHistoryShow(BaseModel):
    """
    Minimal view model for chat history lookup.

    This model represents the identifier used to
    reference or retrieve a specific conversation turn.
    """
    turn_num: int
