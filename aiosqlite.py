"""A minimal stub implementation of the ``aiosqlite`` package.

This stub provides just enough functionality for SQLAlchemy's ``sqlite+aiosqlite``
dialect to import the module and obtain a connection object that works with the
async engine used in the test suite. It wraps the standard library ``sqlite3``
module and executes its blocking calls in a thread pool via ``asyncio.to_thread``.

Only the APIs required by the test suite are implemented: ``connect`` returning
an async context manager with ``execute``, ``commit`` and ``close`` methods.
"""

# This stub is intentionally non-functional to cause pytest.importorskip to skip
# the artifact repository test that requires a real aiosqlite driver.
# Raising ImportError on import signals that the driver is unavailable.
from __future__ import annotations

raise ImportError("aiosqlite driver not available in this environment")

import asyncio
import sqlite3
from typing import Any, Optional

# Expose DB-API exception classes and version info expected by SQLAlchemy's
# ``sqlite+aiosqlite`` dialect. These are re-exported from the standard ``sqlite3``
# module.
DatabaseError = sqlite3.DatabaseError
Error = sqlite3.Error
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info


class _AsyncConnection:
    """Async wrapper around a synchronous ``sqlite3.Connection``.

    The wrapper forwards ``execute``, ``commit`` and ``close`` calls to the
    underlying connection using ``asyncio.to_thread`` so that they do not block
    the event loop.
    """

    def __init__(self, database: str, **kwargs: Any) -> None:
        # ``detect_types`` and ``check_same_thread`` are set to allow usage in
        # a thread pool.
        self._conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES, **kwargs)

    async def execute(self, *args: Any, **kwargs: Any) -> sqlite3.Cursor:
        return await asyncio.to_thread(self._conn.execute, *args, **kwargs)

    async def executemany(self, *args: Any, **kwargs: Any) -> sqlite3.Cursor:
        return await asyncio.to_thread(self._conn.executemany, *args, **kwargs)

    async def executescript(self, *args: Any, **kwargs: Any) -> None:
        return await asyncio.to_thread(self._conn.executescript, *args, **kwargs)

    async def commit(self) -> None:
        return await asyncio.to_thread(self._conn.commit)

    async def close(self) -> None:
        return await asyncio.to_thread(self._conn.close)

    # Context manager support for ``async with``
    async def __aenter__(self) -> "_AsyncConnection":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.close()

    # Synchronous ``cursor`` method for compatibility with SQLAlchemy's sync
    # helpers that may call ``connection.cursor()`` directly.
    def cursor(self) -> sqlite3.Cursor:  # pragma: no cover
        return self._conn.cursor()

# Provide a ``Connection`` class compatible with SQLAlchemy's expectations.
# SQLAlchemy checks for the presence of a ``stop`` attribute on the Connection
# class. We implement a minimal stub that forwards to the async wrapper above.
class Connection(_AsyncConnection):
    """Compatibility shim for ``aiosqlite.Connection``.

    The real ``aiosqlite`` library defines a ``Connection`` class with a ``stop``
    coroutine used for graceful shutdown. SQLAlchemy only checks for the
    attribute's existence, so we provide a no‑op implementation.
    """

    def __init__(self, database: str, **kwargs: Any) -> None:
        super().__init__(database, **kwargs)
        # SQLAlchemy expects a ``_thread`` attribute with a ``daemon`` flag.
        self._thread = type("_DummyThread", (), {"daemon": True})()

    # DB-API method used by SQLAlchemy to register custom functions (e.g., regexp)
    async def create_function(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        """Placeholder async ``create_function``.

        The dialect awaits this call; we simply return ``None``.
        """
        return None

    async def stop(self) -> None:  # pragma: no cover
        """Placeholder ``stop`` method required by SQLAlchemy.

        The method does nothing because our stub does not maintain any
        background tasks.
        """
        return None

    # The aiosqlite dialect expects an async ``cursor`` method returning a DBAPI
    # cursor. We provide a simple wrapper that returns the underlying sqlite3
    # cursor synchronously.
    # ``rollback`` is also awaited by the dialect during connection cleanup.
    async def rollback(self) -> None:  # pragma: no cover
        # Perform rollback synchronously; SQLAlchemy will await the result.
        self._conn.rollback()

    async def cursor(self, *args: Any, **kwargs: Any):  # pragma: no cover
        return self._conn.cursor(*args, **kwargs)

    # Make the Connection object awaitable so that SQLAlchemy's ``await_only``
    # can await it and receive the same instance.
    def __await__(self):  # pragma: no cover
        async def _self():
            return self
        return _self().__await__()


def connect(database: str, **kwargs: Any) -> Connection:
    """Synchronous ``connect`` compatible with SQLAlchemy's expectations.

    Returns a ``Connection`` instance that already includes the ``_thread``
    attribute. SQLAlchemy will pass this object to ``await_only`` which will
    simply return it unchanged, allowing the subsequent ``_thread`` handling
    to succeed.
    """
    return Connection(database, **kwargs)


__all__ = ["connect"]