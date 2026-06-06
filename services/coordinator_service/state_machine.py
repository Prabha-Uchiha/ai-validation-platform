from platform_core.schemas.execution import ExecutionState


VALID_TRANSITIONS = {
    ExecutionState.INITIALIZED: [
        ExecutionState.ANALYZING,
    ],
    ExecutionState.ANALYZING: [
        ExecutionState.PLANNING,
    ],
    ExecutionState.PLANNING: [
        ExecutionState.PROVISIONING,
    ],
    ExecutionState.PROVISIONING: [
        ExecutionState.EXECUTING,
    ],
    ExecutionState.EXECUTING: [
        ExecutionState.DIAGNOSING,
    ],
    ExecutionState.DIAGNOSING: [
        ExecutionState.RETRYING,
        ExecutionState.REPORTING,
    ],
    ExecutionState.RETRYING: [
        ExecutionState.EXECUTING,
    ],
    ExecutionState.REPORTING: [
        ExecutionState.COMPLETED,
    ],
}


class InvalidTransition(Exception):
    pass


class WorkflowStateMachine:
    def transition(
        self,
        current: ExecutionState,
        target: ExecutionState,
    ) -> ExecutionState:

        allowed = VALID_TRANSITIONS.get(current, [])

        if target not in allowed:
            raise InvalidTransition(
                f"Invalid transition {current} -> {target}"
            )

        return target