"""Base contract for all tools.

The contract defines the *shape* of a tool's input and output models.  It is
intentionally minimal – concrete tools subclass it and provide ``Input`` and
``Output`` Pydantic models.  The base class supplies helper methods for
validation that are deterministic and side‑effect free, which satisfies the
replay‑safe requirement.
"""

from __future__ import annotations

from abc import ABC
from typing import Any, Type, ClassVar

from pydantic import BaseModel


class BaseToolContract(ABC):
    """Abstract base class for tool contracts.

    Concrete subclasses must set the ``Input`` and ``Output`` class variables to
    concrete ``BaseModel`` subclasses.  Using ``ClassVar`` makes the intent clear
    to type‑checkers and avoids the ``property``‑related mypy error.
    """

    # Sub‑classes should override these with actual ``BaseModel`` subclasses.
    Input: ClassVar[Type[BaseModel] | None] = None
    Output: ClassVar[Type[BaseModel] | None] = None

    @classmethod
    def validate_input(cls, data: dict[str, Any]) -> BaseModel:
        """Validate *data* against the ``Input`` model.

        ``Input`` may be ``None`` for abstract base classes; in that case a
        ``RuntimeError`` is raised to indicate misuse.
        """
        model = cls.Input
        # Support subclasses that define ``Input`` as a @property returning a model.
        if isinstance(model, property):
            model = model.fget(cls)  # type: ignore[arg-type]
        if model is None:
            raise RuntimeError("Input model not defined for this tool contract")
        return model(**data)

    @classmethod
    def validate_output(cls, data: dict[str, Any]) -> BaseModel:
        """Validate *data* against the ``Output`` model.

        ``Output`` may be ``None`` for abstract base classes; a ``RuntimeError``
        is raised if validation is attempted without a concrete model.
        """
        model = cls.Output
        if isinstance(model, property):
            model = model.fget(cls)  # type: ignore[arg-type]
        if model is None:
            raise RuntimeError("Output model not defined for this tool contract")
        return model(**data)

    @classmethod
    def resolve_contract(cls, import_path: str) -> Type["BaseToolContract"]:
        """Resolve a fully‑qualified import path to a ``BaseToolContract`` subclass.

        The ``ToolDefinition`` stores the contract as a string like
        ``"my.module.MyContract"``. This helper imports the module and returns the
        class object, raising ``ImportError`` if the path is invalid.
        """
        module_path, _, attr = import_path.rpartition(".")
        if not module_path:
            raise ImportError(f"Invalid import path: {import_path}")
        module = __import__(module_path, fromlist=[attr])
        contract = getattr(module, attr)
        if not issubclass(contract, BaseToolContract):
            raise TypeError("Resolved contract does not inherit BaseToolContract")
        return contract
