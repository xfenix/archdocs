fastarch
===
[![CI Pipeline](https://github.com/xfenix/fastarch/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/xfenix/fastarch/actions/workflows/ci.yaml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/xfenix/fastarch/main/.github/badges/coverage.json)](https://xfenix.github.io/fastarch/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

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
* **Kubernetes** — how the traffic gets in (ingress hosts and TLS, service type and port),
  how the service scales (workload kind, replicas, HPA range and its CPU target), what it
  is given (cpu, RAM and GPU requests and limits), how it is configured (ConfigMaps and
  Secrets, as environment or as volumes) and what it persists (volume claims and their size)

Kubernetes manifests are read straight from your repository, no `helm template` run and no
extra dependency: both a Helm chart and a plain directory of manifests work, and templated
`{{ ... }}` values are simply skipped in favour of what `values.yaml` says. They are looked
up recursively under `root_dir` and, if nothing is there, a couple of directories above it —
never outside of the repository your sources live in. Set `kubernetes_dir` when your layout
differs; a relative path is taken from `root_dir`, not from the working directory of the
process:

```python
add_architecture_doc_routes(
    app,
    arch_settings=SettingsForFastarch(
        root_dir="src/",
        service_name="my-service",
        kubernetes_dir="deploy/my-chart/",
    ),
)
```

How it looks
===
fastarch renders your architecture as an interactive Mermaid diagram served
directly from your application. The page shows your service as the central node
with edges to every detected dependency: incoming REST clients, outgoing HTTP
calls, databases, caches, message brokers and task queues.

<img src="./screenshot.png" alt="architecture page served by fastarch" width="900"/>

The screenshot above is the page of `tests/showcase`, an example application that
uses everything from the list above at once, taken as the browser draws it. That
example and its FastAPI and Litestar neighbours are served by the playground, so
you can click through the same pages yourself:

```shell
just playground
```

It starts on <a href="http://127.0.0.1:8000/">127.0.0.1:8000</a> and lists every
example it serves.
