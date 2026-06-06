from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Event(BaseModel):
    event_id: UUID
    execution_id: UUID
    timestamp: datetime
    event_type: str
    correlation_id: str


class ExecutionStarted(Event):
    repository_url: str


class StateTransitioned(Event):
    from_state: str
    to_state: str