from pydantic import BaseModel


class RunPytestInput(BaseModel):
    path: str
    timeout_seconds: int
    retry_budget: int


class RunPytestOutput(BaseModel):
    success: bool
    duration_ms: int
    logs_path: str