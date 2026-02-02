# standard
from typing import Any
from uuid import UUID, uuid4

# third
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """
    Schema for agent request.
    """
    run_id: UUID = Field(default_factory=uuid4)
    input: str
    context: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    """
    Schema for agent response.
    """
    run_id: UUID
    output: str
    metadata: dict[str, Any] = {}
