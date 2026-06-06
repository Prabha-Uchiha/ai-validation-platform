"""Tool related enumerations.

This module defines strict ``Enum`` classes that describe the capabilities
and runtime status of a tool.  The enums are deliberately simple – they are
used only for type‑checking and for persisting deterministic values in the
database.  No business logic is attached.
"""

from __future__ import annotations

import enum


class ToolCapability(str, enum.Enum):
    """Capability categories a tool can belong to.

    The values are stored as strings so they can be persisted directly in a
    relational column or a JSON document without additional conversion.
    """

    TEST = "test"
    BUILD = "build"
    DEPLOY = "deploy"
    ANALYZE = "analyze"


class ToolStatus(str, enum.Enum):
    """Runtime status of a tool execution.

    The enum mirrors the possible outcomes of a sandboxed run.  It is kept
    deterministic – the same input will always map to the same status when
    the tool is deterministic.
    """

    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
