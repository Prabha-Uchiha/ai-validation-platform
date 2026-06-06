from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ExecutionState(str, Enum):
    INITIALIZED = "initialized"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    PROVISIONING = "provisioning"
    EXECUTING = "executing"
    DIAGNOSING = "diagnosing"
    RETRYING = "retrying"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionContext(BaseModel):
    execution_id: UUID
    repository_url: str
    branch: str
    state: ExecutionState