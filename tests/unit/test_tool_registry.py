"""Unit tests for the in‑memory :class:`ToolRegistry`.

The tests cover registration, lookup, listing, and payload validation.  A
minimal dummy contract is defined inline to avoid external dependencies.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from platform_core.contracts.base_tool_contract import BaseToolContract
from platform_core.contracts.tool_definition import ToolDefinition
from platform_core.contracts.tool_registry import ToolRegistry


class DummyContract(BaseToolContract):
    class Input(BaseModel):
        a: int
        b: str

    class Output(BaseModel):
        result: str

    # Assign class variables for the registry to discover
    Input = Input
    Output = Output


def test_register_and_get_definition() -> None:
    registry = ToolRegistry()
    definition = ToolDefinition(
        tool_id="dummy",
        name="Dummy Tool",
        capability="test",  # type: ignore[arg-type]
        version="1.0",
        contract="tests.unit.test_tool_registry.DummyContract",
    )
    registry.register(definition)
    fetched = registry.get_definition("dummy")
    assert fetched.tool_id == "dummy"
    assert fetched.name == "Dummy Tool"


def test_get_contract_and_validation() -> None:
    registry = ToolRegistry()
    definition = ToolDefinition(
        tool_id="dummy",
        name="Dummy Tool",
        capability="test",  # type: ignore[arg-type]
        version="1.0",
        contract="tests.unit.test_tool_registry.DummyContract",
    )
    registry.register(definition)
    contract = registry.get_contract("dummy")
    assert contract is DummyContract
    # Valid payload passes
    registry.validate_tool("dummy", {"a": 5, "b": "x"})
    # Invalid payload raises ValidationError
    with pytest.raises(ValidationError):
        registry.validate_tool("dummy", {"a": "bad", "b": "x"})


def test_list_and_missing_tool() -> None:
    registry = ToolRegistry()
    definition = ToolDefinition(
        tool_id="dummy",
        name="Dummy Tool",
        capability="test",  # type: ignore[arg-type]
        version="1.0",
        contract="tests.unit.test_tool_registry.DummyContract",
    )
    registry.register(definition)
    assert "dummy" in registry.list_tools()
    with pytest.raises(KeyError):
        registry.get_definition("unknown")
