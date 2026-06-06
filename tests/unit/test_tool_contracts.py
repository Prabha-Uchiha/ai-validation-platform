"""Unit tests for the tool contract models introduced in Sprint 1.

The tests verify that the Pydantic models enforce strict typing, that the
enumerations accept only defined values, and that the ``BaseToolContract``
validation helpers work as expected.  No external services are required.
"""

from __future__ import annotations

import pytest
from uuid import uuid4

from platform_core.contracts.base_tool_contract import BaseToolContract
from platform_core.contracts.tool_enums import ToolCapability, ToolStatus
from platform_core.contracts.tool_models import ToolRequest, ToolResult


class DummyToolContract(BaseToolContract):
    """Concrete contract for testing validation helpers.

    The ``Input`` and ``Output`` class variables are set to simple Pydantic
    models.  This avoids the need for property definitions and satisfies the
    type‑checker.
    """

    from pydantic import BaseModel

    class _Input(BaseModel):
        a: int
        b: str

    class _Output(BaseModel):
        result: str

    Input = _Input
    Output = _Output


def test_tool_enums_accept_valid_values() -> None:
    assert ToolCapability.TEST.value == "test"
    assert ToolStatus.SUCCESS.value == "success"


def test_tool_request_validation() -> None:
    req = ToolRequest(
        execution_id=uuid4(),
        tool_id="dummy",
        payload={"a": 1, "b": "x"},
        correlation_id="cid-123",
    )
    assert req.tool_id == "dummy"
    assert isinstance(req.payload, dict)


def test_tool_result_validation() -> None:
    res = ToolResult(
        execution_id=uuid4(),
        tool_id="dummy",
        status=ToolStatus.SUCCESS,
        output={"result": "ok"},
        correlation_id="cid-123",
    )
    assert res.status == ToolStatus.SUCCESS
    assert res.output["result"] == "ok"


def test_base_tool_contract_validation_helpers() -> None:
    # Valid input should parse without error
    data = {"a": 10, "b": "hello"}
    parsed = DummyToolContract.validate_input(data)
    assert parsed.a == 10
    assert parsed.b == "hello"

    # Invalid input should raise ValidationError
    with pytest.raises(Exception):
        DummyToolContract.validate_input({"a": "not an int", "b": "x"})
