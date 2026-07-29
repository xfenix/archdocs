fastarch
===
<img src="./logo.svg" alt="fastarch logo" width="300"/>


This project allows you to achieve something like OpenAPI + SwaggerUI in fastapi/litestar only for architecture.
Core principles are:
* we do love code-first approach
* you dont need to modify your codebase (except library and web framework binding once) or/and add some ugly decorators, comments and other meta staff, library automatically searches for all necessary things, at max it wants to add couple of config options

Quickstart
===
* install package `uv add fastarch`
* connect it to your application:

    FastAPI:
    ```python
    from fastapi import FastAPI
    from fastarch.integrations.fastapi import add_architecture_doc_routes
    from fastarch.main import SettingsForFastarch

    app = FastAPI()

    add_architecture_doc_routes(
        app,
        arch_settings=SettingsForFastarch(
            root_dir="src/",
            service_name="my-service",
        ),
    )
    ```

    Litestar:
    ```python
    from litestar import Litestar
    from fastarch.integrations.litestar import add_architecture_doc_routes
    from fastarch.main import SettingsForFastarch

    app = Litestar()

    add_architecture_doc_routes(
        app,
        arch_settings=SettingsForFastarch(
            root_dir="src/",
            service_name="my-service",
        ),
    )
    ```

    `root_dir` is the directory that fastarch scans for your source code, and
    `service_name` is the label used for your service in the generated diagram.
    Both integrations expose the same `add_architecture_doc_routes` signature and
    serve the diagram at `route_path` (defaults to `/docs/architecture/`).
* go to <a href="http://127.0.0.1:8000/docs/architecture/">/docs/architecture/</a>
* enjoy your schemas

Supported technologies
===
fastarch scans your source code and automatically detects:
* **HTTP endpoints** — FastAPI and Litestar routes (incoming REST methods)
* **Application servers** — granian, uvicorn, gunicorn (including its worker class), hypercorn,
  daphne, waitress and the rest of the ASGI/WSGI family, with worker count, port, TLS and HTTP/2
* **HTTP clients** — httpx, aiohttp, requests, niquests (outgoing calls)
* **Databases** — SQLAlchemy (async engines, pooling, PostgreSQL/asyncpg, and more)
* **Caching** — Redis (plain and sentinel connections)
* **Messaging queues** — FastStream
* **Task queues** — Celery, Taskiq, Arq, RQ, Dramatiq, Huey
* **Kubernetes / Helm** — ingress hosts and TLS, service type, replica count and HPA range

Helm charts are read straight from your repository, no `helm template` run and no extra
dependency. The chart is found next to your code — inside `root_dir` or in the usual
neighbour locations (`deploy/`, `helm/`, `charts/`, `.helm/`) — and never outside of the
project `root_dir` belongs to. Set `helm_chart_dir` when your layout differs; a relative
path is taken from `root_dir`, not from the working directory of the process:

```python
add_architecture_doc_routes(
    app,
    arch_settings=SettingsForFastarch(
        root_dir="src/",
        service_name="my-service",
        helm_chart_dir="deploy/my-chart/",
    ),
)
```

How it looks
===
fastarch renders your architecture as an interactive Mermaid diagram served
directly from your application. The page shows your service as the central node
with edges to every detected dependency: incoming REST clients, outgoing HTTP
calls, databases, caches, message brokers and task queues.
