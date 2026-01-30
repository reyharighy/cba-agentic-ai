# standard
from datetime import datetime

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
    sql_query: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)


class ShortMemoryCreate(BaseModel):
    turn_num: int
    summary: str
    sql_query: str

    def __call__(self) -> ShortMemory:
        """
        Docstring for __call__

        :param self: Description
        :return: Description
        :rtype: ShortMemory
        """
        return ShortMemory(
            turn_num=self.turn_num,
            summary=self.summary,
            sql_query=self.sql_query,
        )


class ShortMemoryShow(BaseModel):
    """
    Docstring for ShortMemoryShow
    """

    turn_num: int
