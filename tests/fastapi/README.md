Fastapi boilerplate
==
This is a part of project generated only for integration testing.

Generated from https://github.com/igorbenav/FastAPI-boilerplate

See [./tests/](./tests/), other parts is just boilerplate-based generated project suitable for test purposes.

`src/integrations/` is not from the boilerplate: it is hand written to give the parsers the
technologies the boilerplate has no use for — requests and niquests clients, a Redis Cluster
cache, RQ and Huey queues, FastStream over NATS and Redis. Together with `tests/litestar` it
covers everything archdocs can detect, and the playground (`just playground`) serves both.
