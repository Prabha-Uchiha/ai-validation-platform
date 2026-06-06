import pytest

from platform_core.schemas.execution import ExecutionState
from services.coordinator_service.state_machine import (
    InvalidTransition,
    WorkflowStateMachine,
)


def test_valid_transition() -> None:
    machine = WorkflowStateMachine()

    result = machine.transition(
        ExecutionState.INITIALIZED,
        ExecutionState.ANALYZING,
    )

    assert result == ExecutionState.ANALYZING


def test_invalid_transition() -> None:
    machine = WorkflowStateMachine()

    with pytest.raises(InvalidTransition):
        machine.transition(
            ExecutionState.INITIALIZED,
            ExecutionState.EXECUTING,
        )