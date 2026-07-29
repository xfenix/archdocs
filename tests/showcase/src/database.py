"""Primary database of the showcase service."""

import typing

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for the models of the showcase service."""


DATABASE_URL: typing.Final = "postgresql+asyncpg://showcase:password@pg-primary:5432/orders?target_session_attrs=read-write"

async_engine: typing.Final = create_async_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=10)

async_session_maker: typing.Final = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    """Open a session to the primary database."""
    async with async_session_maker() as session:
        yield session
