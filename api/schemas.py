# third
from pydantic import BaseModel


class AgentRequest(BaseModel):
    """
    Schema for agent request.
    """

    input: str
