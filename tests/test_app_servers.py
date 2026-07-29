import pathlib
import types
import typing

import pytest

from fastarch.main import SettingsForFastarch
from tests.served_page import extract_diagram, render_architecture_page


# The application server is what the outside world talks to, so it is drawn on the incoming
# edge instead of a node of its own. Detection stays narrow for libraries that merely carry a
# server: gevent, eventlet, werkzeug and tornado are imported for a dozen unrelated reasons,
# so nothing but their serving module counts, otherwise every project using them would be
# drawn as if it served traffic through them.
_SERVICE_NAME: typing.Final = "app-svc"
_SERVED_BY_LABEL: typing.Final = "Served by"
_SERVER_SOURCES: typing.Final = types.MappingProxyType(
    {
        "granian": "import granian\n\ngranian.Granian('src.main:app').serve()\n",
        "uvicorn": "import uvicorn\n\nuvicorn.run('src.main:app')\n",
        "gunicorn": "from gunicorn.app.base import BaseApplication\n",
        "hypercorn": "from hypercorn.asyncio import serve\n",
        "daphne": "from daphne.server import Server\n",
        "waitress": "from waitress import serve\n",
        "uwsgi": "import uwsgi\n",
        "mod_wsgi": "from mod_wsgi import server\n",
        "bjoern": "import bjoern\n",
        "meinheld": "from meinheld import server\n",
        "cheroot": "from cheroot.wsgi import Server\n",
        "tornado": "import tornado.httpserver\n",
        "gevent": "from gevent.pywsgi import WSGIServer\n",
        "eventlet": "import eventlet.wsgi\n",
        "werkzeug": "from werkzeug.serving import run_simple\n",
        "wsgiref": "from wsgiref.simple_server import make_server\n",
    },
)
_GRANIAN_SOURCE: typing.Final = """import granian
from granian.constants import HTTPModes, Interfaces

granian.Granian(
    "src.main:app",
    port=8000,
    workers=4,
    interface=Interfaces.ASGI,
    http=HTTPModes.http2,
    ssl_cert="/etc/tls/tls.crt",
).serve()
"""
_GRANIAN_EDGE: typing.Final = '    external_client --> |"Served by granian, 4 workers, port 8000, TLS, HTTP/2"| app_svc'
_GUNICORN_CONFIG_SOURCE: typing.Final = """bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn_worker.UvicornWorker"
"""
_GUNICORN_EDGE: typing.Final = (
    '    external_client --> |"Served by gunicorn, uvicorn, single worker, port 8000"| app_svc'
)
_SOURCE_WITHOUT_SERVER: typing.Final = """import gevent
import tornado.httpclient
from werkzeug.datastructures import Headers

import fastapi

app = fastapi.FastAPI()
"""


def _render_diagram(project_path: pathlib.Path, source_code: str, /) -> str:
    (project_path / "main.py").write_text(source_code)
    return extract_diagram(
        render_architecture_page(SettingsForFastarch(root_dir=project_path, service_name=_SERVICE_NAME)),
    )


@pytest.mark.parametrize("server_name", _SERVER_SOURCES)
def test_every_supported_server_reaches_diagram(tmp_path: pathlib.Path, server_name: str) -> None:
    assert f'    external_client --> |"{_SERVED_BY_LABEL} {server_name}"| app_svc' in _render_diagram(
        tmp_path,
        _SERVER_SOURCES[server_name],
    )


def test_server_properties_reach_the_edge_label(tmp_path: pathlib.Path) -> None:
    assert _GRANIAN_EDGE in _render_diagram(tmp_path, _GRANIAN_SOURCE)


def test_worker_class_names_both_servers(tmp_path: pathlib.Path) -> None:
    assert _GUNICORN_EDGE in _render_diagram(tmp_path, _GUNICORN_CONFIG_SOURCE)


def test_carrier_library_is_not_a_server(tmp_path: pathlib.Path) -> None:
    assert _SERVED_BY_LABEL not in _render_diagram(tmp_path, _SOURCE_WITHOUT_SERVER)
