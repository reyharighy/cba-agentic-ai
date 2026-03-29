# standard
from datetime import datetime

# third-party
from pydantic import (
    BaseModel,
    Field,
)


class ShortMemory(BaseModel):
    """
    Schema for short-term memory summary.
    """

    turn_num: int = Field(ge=1)
    summary: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)


class ShortMemoryCreate(BaseModel):
    turn_num: int
    summary: str

    def __call__(self) -> ShortMemory:
        """
        Convert ShortMemoryCreate to ShortMemory.
        """
        return ShortMemory(
            turn_num=self.turn_num,
            summary=self.summary,
        )


class ShortMemoryShow(BaseModel):
    """
    Schema for showing short-term memory summary.
    """

    turn_num: int
