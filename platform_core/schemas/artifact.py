"""Pydantic schema for immutable artifacts.

The schema mirrors the SQLAlchemy ``ArtifactModel`` and is used as the return
type of the repository methods.  ``orm_mode`` is enabled to allow ``from_orm``
construction.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ArtifactMetadata(BaseModel):
    """Typed metadata for an artifact.

    This schema replaces the previously untyped ``Dict[str, Any]`` metadata
    field, providing a deterministic structure that can be validated and
    versioned.
    """

    # Example fields – can be extended as needed by the system.
    tags: Optional[list[str]] = Field(default=None, description="Optional list of tags")
    description: Optional[str] = Field(default=None, description="Human‑readable description")
    extra: Optional[Dict[str, Any]] = Field(default=None, description="Arbitrary additional data")


class ArtifactSchema(BaseModel):
    artifact_id: uuid.UUID = Field(..., description="Primary key of the artifact")
    execution_id: uuid.UUID = Field(..., description="Execution to which the artifact belongs")
    artifact_type: str = Field(..., description="Logical type of the artifact")
    artifact_uri: str = Field(..., description="Location of the stored artifact payload")
    artifact_metadata: Optional[ArtifactMetadata] = Field(default=None, description="Typed artifact metadata")
    created_at: datetime = Field(..., description="Timestamp of creation (UTC)")

    class Config:
        orm_mode = True
