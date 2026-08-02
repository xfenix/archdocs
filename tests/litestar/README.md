# Litestar Test Application

Mock Litestar application for testing archdocs integration. The same sources are served by
the playground (`just playground`), so this application and its FastAPI neighbour split every
supported technology between them — half of the list lives here.

## Features

- **HTTP API**: Multiple endpoints with various HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **SQLAlchemy**: Async engine plus a pooled sync engine over two replica hosts
- **Redis**: Cache layer with a retrying plain client and a Sentinel backed one
- **HTTP Clients**: External API calls using httpx and aiohttp
- **Task Queues**: Background tasks using Celery, Taskiq and Dramatiq
- **Messaging**: FastStream consumers and publishers over RabbitMQ and Kafka

## Structure

```
src/
├── main.py              # Application entry point
├── database.py          # SQLAlchemy async configuration
├── database_replica.py  # Pooled sync engine over replicas
├── cache.py             # Redis configuration
├── cache_sentinel.py    # Redis Sentinel configuration
├── tasks.py             # Task queues (Celery, Taskiq, Dramatiq)
├── messaging.py         # FastStream brokers (RabbitMQ, Kafka)
├── http_clients.py      # HTTP clients (httpx, aiohttp)
└── routes/
    ├── users.py         # User endpoints
    └── items.py         # Item endpoints
```
