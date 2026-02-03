# third
from pydantic import BaseModel


class AgentRequest(BaseModel):
    """
    Schema for agent request.
    """

    turn_num: int
    input: str
