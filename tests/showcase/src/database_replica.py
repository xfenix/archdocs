"""Read only replicas of the showcase service."""

import typing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


replica_engine: typing.Final = create_engine(
    'postgresql+psycopg://showcase:password@pg-replica-one:5432,pg-replica-two:5432/orders',
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)

replica_session_maker: typing.Final = sessionmaker(bind=replica_engine, expire_on_commit=False)


def count_orders() -> int:
    """Count orders on a read only replica."""
    with replica_session_maker() as session:
        return session.execute("select count(*) from orders").scalar_one()
