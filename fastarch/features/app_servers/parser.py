import re as py_re
import types
import typing

from fastarch import prefilter, settings
from fastarch.features.app_servers.const import ApplicationServerEnum, ApplicationServerFeatures


_NAMED_BY_MODULE_TEMPLATE: typing.Final = r"\b(?:from|import)\s+{module_name}\b|\b{module_name}\s+(?:--\w|[\w.]+:\w+)"


@typing.final
class _ServerSignature(typing.NamedTuple):
    """Empty `pattern` means the server is named by its own module, empty `literals` — by its own name."""

    pattern: str = ""
    literals: tuple[str, ...] = ()


# Servers with an explicit pattern ship it inside a library that is imported for a dozen other
# reasons, so only the serving module counts: a bare `import gevent` is not a wsgi server,
# `gevent.pywsgi` is. Literals are spelled out only where the pattern can match without the
# server's own name in the source — a pattern and its literals have to agree, see `prefilter`.
_SERVER_SIGNATURES: typing.Final = types.MappingProxyType(
    {
        ApplicationServerEnum.granian_server: _ServerSignature(),
        ApplicationServerEnum.uvicorn_server: _ServerSignature(),
        ApplicationServerEnum.gunicorn_server: _ServerSignature(),
        ApplicationServerEnum.hypercorn_server: _ServerSignature(),
        ApplicationServerEnum.daphne_server: _ServerSignature(),
        ApplicationServerEnum.waitress_server: _ServerSignature(),
        ApplicationServerEnum.uwsgi_server: _ServerSignature(),
        ApplicationServerEnum.mod_wsgi_server: _ServerSignature(),
        ApplicationServerEnum.bjoern_server: _ServerSignature(),
        ApplicationServerEnum.meinheld_server: _ServerSignature(),
        ApplicationServerEnum.cheroot_server: _ServerSignature(),
        ApplicationServerEnum.tornado_server: _ServerSignature(r"\btornado\.(?:httpserver|web|ioloop)\b"),
        ApplicationServerEnum.gevent_server: _ServerSignature(r"\bgevent\.pywsgi\b"),
        ApplicationServerEnum.eventlet_server: _ServerSignature(r"\beventlet\.wsgi\b"),
        ApplicationServerEnum.werkzeug_server: _ServerSignature(
            r"\bwerkzeug\.serving\b|\brun_simple\s*\(",
            ("werkzeug", "run_simple"),
        ),
        ApplicationServerEnum.wsgiref_server: _ServerSignature(r"\bwsgiref\.simple_server\b"),
    },
)
_COMPILED_SERVER_SIGNATURES: typing.Final = tuple(
    (
        one_server.value,
        one_signature.literals or (one_server.value,),
        py_re.compile(
            one_signature.pattern or _NAMED_BY_MODULE_TEMPLATE.format(module_name=one_server.value),
            flags=settings.TYPICAL_RE_FLAGS,
        ),
    )
    for one_server, one_signature in _SERVER_SIGNATURES.items()
)
_WORKER_CLASS_LITERALS: typing.Final = ("worker_class", "--worker-class")
_WORKER_CLASS_PATTERN: typing.Final = py_re.compile(
    r"(?:worker_class\s*=|--worker-class)[\s=\"']*(?P<worker_class>[\w.]+)",
    flags=settings.TYPICAL_RE_FLAGS,
)
_WORKERS_COUNT_PATTERN: typing.Final = py_re.compile(
    r"(?:workers\s*=|--workers|\s-w)[\s=\"']*(?P<found_number>\d{1,3})\b",
    flags=settings.TYPICAL_RE_FLAGS,
)
_LISTEN_PORT_PATTERN: typing.Final = py_re.compile(
    r"(?:(?:port\s*=|--port)[\s=\"']*|(?:bind|--bind)[\s=\"']*[\w.\[\]]*:)(?P<found_number>\d{2,5})\b",
    flags=settings.TYPICAL_RE_FLAGS,
)
_TLS_PATTERN: typing.Final = py_re.compile(
    r"\bssl_cert\w*\b|\bssl_key\w*\b|\bcertfile\b|\bkeyfile\b|\bssl_context\b|--ssl-\w+",
    flags=settings.TYPICAL_RE_FLAGS,
)
_HTTP2_PATTERN: typing.Final = py_re.compile(
    r"\bhttp2\b|\bhttp\s*=\s*[\"']?2\b|--http[\s=]+2\b",
    flags=settings.TYPICAL_RE_FLAGS,
)


def _read_first_number(number_pattern: py_re.Pattern[str], raw_source: str, /) -> int:
    number_match: typing.Final = number_pattern.search(raw_source)
    if number_match is None:
        return 0
    return int(number_match.group("found_number"))


def _find_servers_behind_worker_class(raw_source: str, lowered_source: str, /) -> set[str]:
    if not prefilter.contains_any_literal(lowered_source, _WORKER_CLASS_LITERALS):
        return set()
    worker_class_match: typing.Final = _WORKER_CLASS_PATTERN.search(raw_source)
    if worker_class_match is None:
        return set()
    worker_class_name: typing.Final = worker_class_match.group("worker_class").lower()
    return {ApplicationServerEnum.gunicorn_server.value} | {
        one_server.value for one_server in ApplicationServerEnum if one_server.value in worker_class_name
    }


def find_application_server_features(raw_source: str) -> ApplicationServerFeatures:
    lowered_source: typing.Final = raw_source.lower()
    servers_found: typing.Final = {
        one_server_name
        for one_server_name, one_literals, one_pattern in _COMPILED_SERVER_SIGNATURES
        if prefilter.contains_any_literal(lowered_source, one_literals) and one_pattern.search(raw_source)
    } | _find_servers_behind_worker_class(raw_source, lowered_source)
    if not servers_found:
        return ApplicationServerFeatures()
    return ApplicationServerFeatures(
        servers_used=frozenset(servers_found),
        workers_count=_read_first_number(_WORKERS_COUNT_PATTERN, raw_source),
        listen_port=_read_first_number(_LISTEN_PORT_PATTERN, raw_source),
        tls_enabled=bool(_TLS_PATTERN.search(raw_source)),
        http2_enabled=bool(_HTTP2_PATTERN.search(raw_source)),
    )
