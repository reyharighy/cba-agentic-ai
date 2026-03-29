# standard
from datetime import datetime
from typing import Literal

# third-party
from pydantic import BaseModel, Field


class ChatHistory(BaseModel):
    """
    Schema for chat history between human and AI.
    """

    turn_num: int = Field(ge=1)
    role: Literal["human", "ai"]
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)


class ChatHistoryCreate(BaseModel):
    turn_num: int
    role: Literal["human", "ai"]
    content: str

    def __call__(self) -> ChatHistory:
        """
        Convert ChatHistoryCreate to ChatHistory.
        """
        return ChatHistory(
            turn_num=self.turn_num,
            role=self.role,
            content=self.content,
        )


class ChatHistoryShow(BaseModel):
    """
    Schema for showing chat history.
    """

    turn_num: int
