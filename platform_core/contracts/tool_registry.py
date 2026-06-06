"""In‑memory tool registry.

The registry stores :class:`ToolDefinition` objects and provides fast lookup of
the associated :class:`BaseToolContract` class.  It is deliberately simple –
only an in‑memory ``dict`` protected by a ``threading.Lock`` is used.  All
operations are deterministic and type‑checked.

Observability is provided via ``structlog`` – each public method logs at the
``INFO`` level with the ``tool_id`` (when applicable) and the action being
performed.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Type, Any, cast

import structlog

from .base_tool_contract import BaseToolContract
from .tool_definition import ToolDefinition

logger = structlog.get_logger(__name__)


class ToolRegistry:
    """Thread‑safe, deterministic registry for tool definitions.

    The registry is a singleton‑style class – an instance can be created
    wherever needed, but all instances share the same underlying storage via a
    class‑level lock and dictionary.  This keeps the implementation simple for
    the sprint while satisfying the *in‑memory only* requirement.
    """

    _store: Dict[str, ToolDefinition] = {}
    _lock = threading.Lock()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def register(self, definition: ToolDefinition | None = None, *, tool_id: str | None = None,
                 name: str | None = None, capability: str | None = None,
                 version: str | None = None, contract: Type[BaseToolContract] | None = None) -> None:
        """Register a new tool.

        This method supports two calling styles for convenience:

        1. ``register(definition)`` – pass a pre‑constructed ``ToolDefinition``.
        2. ``register(tool_id=..., name=..., capability=..., version=..., contract=...)`` –
           provide the individual fields; a ``ToolDefinition`` is constructed
           internally.
        """
        if definition is None:
            if None in (tool_id, name, capability, contract):
                raise ValueError("Insufficient arguments to construct ToolDefinition")
            # ``contract`` can be a class; store its import path as a string.
            contract_path = f"{contract.__module__}.{contract.__qualname__}"
            definition = ToolDefinition(
                tool_id=tool_id,
                name=name,
                capability=capability,  # type: ignore[arg-type]
                version=version,
                contract=contract_path,
            )
        with self._lock:
            self._store[definition.tool_id] = definition
        logger.info("tool_registered", tool_id=definition.tool_id)

    def get_definition(self, tool_id: str) -> ToolDefinition:
        """Return the stored :class:`ToolDefinition` for *tool_id*.

        Raises ``KeyError`` if the tool is not registered.
        """
        with self._lock:
            definition = self._store[tool_id]
        logger.debug("tool_definition_fetched", tool_id=tool_id)
        return definition

    def get_contract(self, tool_id: str) -> Type[BaseToolContract]:
        """Return the contract class associated with *tool_id*.

        The contract class is imported lazily using the fully‑qualified import
        path stored in ``ToolDefinition.contract``.
        """
        definition = self.get_definition(tool_id)
        module_path, _, attr = definition.contract.rpartition(".")
        module = __import__(module_path, fromlist=[attr])
        contract = getattr(module, attr)
        if not issubclass(contract, BaseToolContract):
            raise TypeError("Registered contract does not inherit BaseToolContract")
        logger.debug("tool_contract_resolved", tool_id=tool_id)
        return cast(Type[BaseToolContract], contract)

    def list_tools(self) -> List[str]:
        """Return a list of all registered tool identifiers."""
        with self._lock:
            ids = list(self._store.keys())
        logger.debug("tool_listed", count=len(ids))
        return ids

    def validate_tool(self, tool_id: str, payload: dict[str, Any]) -> None:
        """Validate *payload* against the tool's input contract.

        Raises ``pydantic.ValidationError`` if the payload is invalid and
        ``KeyError`` if the tool is unknown.
        """
        contract = self.get_contract(tool_id)
        contract.validate_input(payload)
        logger.info("tool_payload_validated", tool_id=tool_id)
