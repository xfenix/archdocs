# Litestar Test Application

Mock Litestar application for testing fastarch integration.

## Features

- **HTTP API**: Multiple endpoints with various HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **SQLAlchemy**: Async database with connection pooling and target_session_attrs
- **Redis**: Cache layer with both plain Redis and Sentinel support
- **HTTP Clients**: External API calls using httpx and aiohttp
- **Task Queues**: Background tasks using Celery and Taskiq

## Structure

```
src/
├── main.py              # Application entry point
├── database.py          # SQLAlchemy configuration
├── cache.py             # Redis configuration
├── tasks.py             # Task queues (Celery, Taskiq)
├── http_clients.py      # HTTP clients (httpx, aiohttp)
└── routes/
    ├── users.py         # User endpoints
    └── items.py         # Item endpoints
```
