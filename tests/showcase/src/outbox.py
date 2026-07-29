"""Local outbox of the showcase service."""

import typing

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


OUTBOX_URL: typing.Final = "sqlite+aiosqlite:///./outbox.db"

outbox_engine: typing.Final = create_async_engine(OUTBOX_URL, echo=False)

outbox_session_maker: typing.Final = sessionmaker(bind=outbox_engine, class_=AsyncSession, expire_on_commit=False)


async def get_outbox_session() -> AsyncSession:
    """Open a session to the local outbox."""
    async with outbox_session_maker() as session:
        yield session
