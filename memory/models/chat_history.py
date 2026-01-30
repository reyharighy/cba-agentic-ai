# standard
from datetime import datetime
from typing import Literal

# third-party
from pydantic import BaseModel, Field


class ChatHistory(BaseModel):
    """
    Docstring for ChatHistory
    """

    turn_num: int = Field(ge=1)
    role: Literal["Human", "AI"]
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)


class ChatHistoryCreate(BaseModel):
    turn_num: int
    role: Literal["Human", "AI"]
    content: str

    def __call__(self) -> ChatHistory:
        """
        Docstring for __call__

        :param self: Description
        :return: Description
        :rtype: ChatHistory
        """
        return ChatHistory(
            turn_num=self.turn_num,
            role=self.role,
            content=self.content,
        )


class ChatHistoryShow(BaseModel):
    """
    Docstring for ChatHistoryShow
    """

    turn_num: int
