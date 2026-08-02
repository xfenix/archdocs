# Showcase Application

Mock FastAPI application that uses every technology archdocs can detect at once, so a single
served page shows the whole picture. The playground (`just playground`) serves it next to its
FastAPI and Litestar neighbours, and the screenshot in the root `README.md` is taken from it.

## Features

- **HTTP API**: Order endpoints covering GET, POST, PUT, PATCH and DELETE
- **Application servers**: Granian for local runs with TLS and HTTP/2, gunicorn with uvicorn
  workers in the cluster
- **SQLAlchemy**: Async engine to the primary, a pooled sync engine over two replica hosts
  and a local SQLite outbox
- **Redis**: Async client with retries, a Sentinel backed session storage and a Redis Cluster
- **HTTP Clients**: External calls over httpx, aiohttp, requests and niquests
- **Task Queues**: Background tasks over Celery, Taskiq, Arq, RQ, Dramatiq and Huey
- **Messaging**: FastStream consumers and publishers over RabbitMQ, Kafka, NATS and Redis
- **Kubernetes**: the chart from `tests/kubernetes_fixtures/`, wired in by the playground

## Structure

```
src/
├── main.py              # Application entry point
├── server.py            # Granian entrypoint and the documented gunicorn command
├── database.py          # SQLAlchemy async configuration
├── database_replica.py  # Pooled sync engine over replicas
├── outbox.py            # Local SQLite outbox
├── cache.py             # Redis connections
├── cache_sentinel.py    # Redis Sentinel configuration
├── cache_cluster.py     # Redis Cluster configuration
├── http_clients.py      # HTTP clients (httpx, aiohttp, requests, niquests)
├── messaging.py         # FastStream brokers (RabbitMQ, Kafka, NATS, Redis)
├── tasks.py             # Task queues (Celery, Taskiq, Arq, RQ, Dramatiq, Huey)
└── api/
    └── orders.py        # Order endpoints
```
