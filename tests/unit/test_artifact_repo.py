"""Tests for the ArtifactRepository implementation.

The tests use an in‑memory SQLite database with SQLAlchemy's async engine to
exercise the repository without requiring a real PostgreSQL instance.
"""

from __future__ import annotations

import uuid
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from storage.postgres.database import Base
from storage.postgres.repositories.artifact_repo import ArtifactRepository

import asyncio


@pytest.mark.asyncio
async def test_artifact_repository_crud():
    # Skip test if aiosqlite driver is not installed
    pytest.importorskip("aiosqlite")
    # Set up in‑memory async SQLite engine and session locally
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_maker() as session:
        repo = ArtifactRepository(session)
    exec_id = uuid.uuid4()
    # Create artifact
    created = await repo.create(
        execution_id=exec_id,
        artifact_type="test_type",
        artifact_uri="file://test",
        metadata={"key": "value"},
    )
    assert created.execution_id == exec_id
    assert created.artifact_type == "test_type"
    # Retrieve by ID
    fetched = await repo.get_by_id(created.artifact_id)
    assert fetched is not None
    assert fetched.artifact_id == created.artifact_id
    # List by execution
    listed = await repo.list_by_execution(exec_id)
    assert len(listed) == 1
    assert listed[0].artifact_id == created.artifact_id
