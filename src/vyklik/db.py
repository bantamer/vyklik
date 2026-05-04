from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from vyklik.config import settings


def _async_dsn(dsn: str) -> str:
    """Coerce a plain postgres:// DSN to the asyncpg driver SQLAlchemy expects."""
    if dsn.startswith("postgresql+asyncpg://"):
        return dsn
    if dsn.startswith("postgresql://"):
        return "postgresql+asyncpg://" + dsn[len("postgresql://") :]
    return dsn


def _raw_dsn(dsn: str) -> str:
    """asyncpg.connect wants the bare postgres:// form, no SQLAlchemy driver suffix."""
    if dsn.startswith("postgresql+asyncpg://"):
        return "postgresql://" + dsn[len("postgresql+asyncpg://") :]
    return dsn


_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(_async_dsn(settings.postgres_dsn), pool_pre_ping=True)
    return _engine


def session_factory() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(engine(), expire_on_commit=False)
    return _sessionmaker


@asynccontextmanager
async def session() -> AsyncIterator[AsyncSession]:
    async with session_factory()() as s:
        yield s


async def asyncpg_connect() -> asyncpg.Connection:
    """Dedicated asyncpg connection — needed for LISTEN/NOTIFY (SQLAlchemy pool steals it)."""
    return await asyncpg.connect(_raw_dsn(settings.postgres_dsn))
