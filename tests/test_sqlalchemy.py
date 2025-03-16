import typing


DSN_LIST: typing.Final = {
    "postgresql+psycopg2://user:password@localhost:5432/dbname",
    "postgresql+asyncpg://user:password@/dbname?host=host1:5432&host=host2:5432&host=host3:5432",
    "postgresql+asyncpg://user:password@localhost:5432/dbname?pool_size=10&max_overflow=5&pool_timeout=30&pool_recycle=1800",
    "postgresql+asyncpg://user:password@/dbname?host=host1,host2,host3&target_session_attrs=read-write",
    "postgresql+asyncpg://user:password@/dbname?host=host1,host2,host3&target_session_attrs=read-only",
    "postgresql+psycopg2://user:password@/dbname?host=host1,host2,host3&target_session_attrs=any",
    "postgresql+asyncpg://user:password@localhost:5432/dbname",
}
