import dataclasses
import enum
import typing


@typing.final
class ApplicationServerEnum(enum.Enum):
    granian_server = "granian"
    uvicorn_server = "uvicorn"
    gunicorn_server = "gunicorn"
    hypercorn_server = "hypercorn"
    daphne_server = "daphne"
    waitress_server = "waitress"
    uwsgi_server = "uwsgi"
    mod_wsgi_server = "mod_wsgi"
    bjoern_server = "bjoern"
    meinheld_server = "meinheld"
    cheroot_server = "cheroot"
    tornado_server = "tornado"
    gevent_server = "gevent"
    eventlet_server = "eventlet"
    werkzeug_server = "werkzeug"
    wsgiref_server = "wsgiref"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ApplicationServerFeatures:
    servers_used: frozenset[str] = frozenset()
    workers_count: int = 0
    listen_port: int = 0
    tls_enabled: bool = False
    http2_enabled: bool = False
