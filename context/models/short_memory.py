"""
Docstring for context.short_memory
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
    Docstring for ShortMemory
    """
    turn_num: int = Field(ge=1)
    summary: str = Field(min_length=1)
    sql_query: Optional[str] = Field(min_length=1, default=None)
    created_at: datetime = Field(default_factory=datetime.now)

class ShortMemoryCreate(BaseModel):
    """
    Docstring for ShortMemoryCreate
    """
    turn_num: int
    summary: str
    sql_query: Optional[str]

    def __call__(self) -> ShortMemory:
        """
        Docstring for __call__
        
        :param self: Description
        :return: Description
        :rtype: Any
        """
        return ShortMemory(
            turn_num=self.turn_num,
            summary=self.summary,
            sql_query=self.sql_query
        )

class ShortMemoryShow(BaseModel):
    """
    Docstring for ShortMemoryShow
    """
    turn_num: int
