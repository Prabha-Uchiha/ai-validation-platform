import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID

from platform_core.observability.logging import configure_logging
from storage.postgres.database import async_session_maker
from storage.postgres.repositories.execution_repo import ExecutionRepository
from storage.postgres.repositories.checkpoint_repo import CheckpointRepository
from storage.postgres.repositories.event_repo import EventRepository
from services.coordinator_service.checkpoints import CheckpointManager
from services.coordinator_service.state_machine import WorkflowStateMachine
from services.coordinator_service.coordinator import Coordinator
from event_bus.publishers.publisher import EventPublisher
from event_bus.redis_streams.client import RedisStreamClient

configure_logging()
logger = structlog.get_logger()

app = FastAPI(title="Coordinator Service")

# Dependency Injection Setup
redis_client = RedisStreamClient()
state_machine = WorkflowStateMachine()

class StartExecutionRequest(BaseModel):
    repository_url: str
    branch: str

@app.post("/executions")
async def start_execution(request: StartExecutionRequest) -> dict[str, UUID]:
    async with async_session_maker() as session:
        execution_repo = ExecutionRepository(session)
        checkpoint_repo = CheckpointRepository(session)
        event_repo = EventRepository(session)
        checkpoint_manager = CheckpointManager(checkpoint_repo)

        event_publisher = EventPublisher(event_repo, redis_client)

        coordinator = Coordinator(
            execution_repo=execution_repo,
            event_repo=event_repo,
            checkpoint_manager=checkpoint_manager,
            state_machine=state_machine,
            event_publisher=event_publisher,
        )

        try:
            execution_id = await coordinator.start_execution(
                repository_url=request.repository_url,
                branch=request.branch,
            )
            return {"execution_id": execution_id}
        except Exception as e:
            logger.exception("Failed to start execution", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
    }
