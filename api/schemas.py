# third
from pydantic import BaseModel


class AgentRequest(BaseModel):
    """
    Schema for agent request.
    """

    input: str


class ResumeRequest(BaseModel):
    """
    Schema for resuming an interrupted agent run.
    """

    thread_id: str
    input: str
