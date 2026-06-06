"""Pydantic model describing a tool definition.

The model is deliberately *data‑only* – it contains the static metadata that
identifies a tool and its contract classes.  It is used by the registry (which
is out of scope for this sprint) and by the execution runtime when persisting
information about which tool was used.
"""

from __future__ import annotations

# No external imports needed; the contract field stores a string path.

from pydantic import BaseModel, Field

from .tool_enums import ToolCapability


class ToolDefinition(BaseModel):
    """Immutable definition of a tool.

    Attributes
    ----------
    tool_id: str
        Unique identifier used throughout the system.
    name: str
        Human readable name.
    capability: ToolCapability
        High‑level category of the tool.
    version: str | None
        Optional semantic version string.
    contract: Type[BaseModel]
        Reference to the Pydantic contract class that validates the tool's
        input payload.  Stored as a string representation for deterministic
        persistence.
    """

    tool_id: str = Field(..., description="Unique identifier for the tool")
    name: str = Field(..., description="Human readable name")
    capability: ToolCapability = Field(..., description="Tool capability category")
    version: str | None = Field(None, description="Optional semantic version")
    contract_version: int = Field(1, description="Version of the contract schema for this tool definition")
    contract: str = Field(
        ..., description="Fully qualified import path of the contract class"
    )
