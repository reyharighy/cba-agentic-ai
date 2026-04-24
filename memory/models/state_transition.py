# standard
import hashlib
import json
from datetime import datetime
from typing import (
    Any,
    Literal,
)

# third-party
from pydantic import (
    BaseModel,
    Field,
)


_PAYLOAD_PREVIEW_MAX_CHARS: int = 256


def redact_payload(payload: dict[str, Any] | None) -> tuple[str | None, int | None, str | None]:
    """
    Redact a payload for the audit log: returns (sha256 hex digest, byte size, short preview).

    The verbatim payload is never persisted; only its digest, size, and a truncated
    preview are kept to support traceable per-run reconstruction without storing
    user prompts, generated SQL, LLM outputs, or sandbox stdout in the clear.
    """
    if payload is None:
        return (None, None, None)

    serialized: str = json.dumps(
        obj=payload,
        default=str,
        sort_keys=True,
        ensure_ascii=False,
    )

    encoded: bytes = serialized.encode("utf-8")
    digest: str = hashlib.sha256(encoded).hexdigest()
    size: int = len(encoded)
    preview: str = serialized[:_PAYLOAD_PREVIEW_MAX_CHARS]

    return (digest, size, preview)


class StateTransition(BaseModel):
    """
    Schema for a persisted graph state transition (audit log row).
    """

    thread_id: str = Field(min_length=1)
    turn_num: int = Field(ge=1)
    sequence_num: int = Field(ge=1)
    node_name: str = Field(min_length=1)
    event_type: Literal["update", "interrupt", "complete", "error"]
    payload_digest: str | None = None
    payload_size: int | None = None
    payload_preview: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class StateTransitionCreate(BaseModel):
    thread_id: str
    turn_num: int
    sequence_num: int
    node_name: str
    event_type: Literal["update", "interrupt", "complete", "error"]
    payload: dict[str, Any] | None = None
    error_message: str | None = None

    def __call__(self) -> StateTransition:
        """
        Convert StateTransitionCreate to StateTransition.
        """
        digest, size, preview = redact_payload(self.payload)

        return StateTransition(
            thread_id=self.thread_id,
            turn_num=self.turn_num,
            sequence_num=self.sequence_num,
            node_name=self.node_name,
            event_type=self.event_type,
            payload_digest=digest,
            payload_size=size,
            payload_preview=preview,
            error_message=self.error_message,
        )


class StateTransitionShow(BaseModel):
    """
    Schema for showing state transitions filtered by thread.
    """

    thread_id: str
