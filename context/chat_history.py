"""
Docstring for context.chat_history
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
    Docstring for ChatHistory
    """
    turn_num: int = Field(ge=1)
    role: Literal["Human", "AI"]
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)

class ChatHistoryCreate(BaseModel):
    """
    Docstring for ChatHistoryCreate
    """
    turn_num: int
    role: Literal["Human", "AI"]
    content: str

    def __call__(self) -> ChatHistory:
        """
        Docstring for __call__
        
        :param self: Description
        :return: Description
        :rtype: Any
        """
        return ChatHistory(
            turn_num=self.turn_num,
            role=self.role,
            content=self.content
        )

class ChatHistoryShow(BaseModel):
    """
    Docstring for ShortMemoryShow
    """
    turn_num: int
