"""Database configuration with SQLAlchemy."""

import typing

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


DATABASE_URL: typing.Final = "postgresql+asyncpg://user:password@localhost:5432/testdb?target_session_attrs=read-write"

async_engine: typing.Final = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
)

async_session_maker: typing.Final = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
    """Get database session."""
    async with async_session_maker() as session:
        yield session
