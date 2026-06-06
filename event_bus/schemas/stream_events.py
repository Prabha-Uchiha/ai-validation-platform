from enum import Enum
import uuid
from pydantic import BaseModel, Field


class StreamName(str, Enum):
    EXECUTION_EVENTS = "execution_events"
    WORKFLOW_EVENTS = "workflow_events"

# Artifact events
class ArtifactEvent(str, Enum):
    ARTIFACT_CREATED = "artifact.created"


class ArtifactCreated(BaseModel):
    artifact_id: uuid.UUID = Field(..., description="ID of the created artifact")
    execution_id: uuid.UUID = Field(..., description="Execution to which the artifact belongs")
    artifact_type: str = Field(..., description="Logical type of the artifact")
    event_version: int = Field(1, description="Version of the ArtifactCreated event schema")
    correlation_id: uuid.UUID = Field(..., description="Correlation ID linking the artifact to the originating tool request")

    class Config:
        orm_mode = True