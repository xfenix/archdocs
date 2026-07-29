"""Read only replicas served by a pooled sync engine."""

import typing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


replica_engine: typing.Final = create_engine(
    'postgresql+psycopg://user:password@replica-one:5432,replica-two:5432/testdb',
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)

replica_session_maker: typing.Final = sessionmaker(bind=replica_engine, expire_on_commit=False)


def count_items() -> int:
    """Count items on a read only replica."""
    with replica_session_maker() as session:
        return session.execute("select count(*) from items").scalar_one()
