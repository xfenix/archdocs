import dataclasses
import re as py_re
import typing

from archdocs import prefilter, settings
from archdocs.features.app_servers.const import ApplicationServerEnum, ApplicationServerFeatures


_NAMED_BY_MODULE_TEMPLATE: typing.Final = r"\b(?:from|import)\s+{module_name}\b|\b{module_name}\s+(?:--\w|[\w.]+:\w+)"


@typing.final
@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class _ServerSignature:
    server_name: str
    prefilter_literals: tuple[str, ...]
    compiled_pattern: py_re.Pattern[str]


def _build_server_signature(
    detected_server: ApplicationServerEnum,
    /,
    *,
    raw_pattern: str = "",
    prefilter_literals: tuple[str, ...] = (),
) -> _ServerSignature:
    return _ServerSignature(
        server_name=detected_server.value,
        prefilter_literals=prefilter_literals or (detected_server.value,),
        compiled_pattern=py_re.compile(
            raw_pattern or _NAMED_BY_MODULE_TEMPLATE.format(module_name=detected_server.value),
            flags=settings.TYPICAL_RE_FLAGS,
        ),
    )


_SERVER_SIGNATURES: typing.Final = (
    _build_server_signature(ApplicationServerEnum.granian_server),
    _build_server_signature(ApplicationServerEnum.uvicorn_server),
    _build_server_signature(ApplicationServerEnum.gunicorn_server),
    _build_server_signature(ApplicationServerEnum.hypercorn_server),
    _build_server_signature(ApplicationServerEnum.daphne_server),
    _build_server_signature(ApplicationServerEnum.waitress_server),
    _build_server_signature(ApplicationServerEnum.uwsgi_server),
    _build_server_signature(ApplicationServerEnum.mod_wsgi_server),
    _build_server_signature(ApplicationServerEnum.bjoern_server),
    _build_server_signature(ApplicationServerEnum.meinheld_server),
    _build_server_signature(ApplicationServerEnum.cheroot_server),
    _build_server_signature(
        ApplicationServerEnum.tornado_server,
        raw_pattern=r"\btornado\.(?:httpserver|web|ioloop)\b",
    ),
    _build_server_signature(ApplicationServerEnum.gevent_server, raw_pattern=r"\bgevent\.pywsgi\b"),
    _build_server_signature(ApplicationServerEnum.eventlet_server, raw_pattern=r"\beventlet\.wsgi\b"),
    _build_server_signature(
        ApplicationServerEnum.werkzeug_server,
        raw_pattern=r"\bwerkzeug\.serving\b|\brun_simple\s*\(",
        prefilter_literals=("werkzeug", "run_simple"),
    ),
    _build_server_signature(ApplicationServerEnum.wsgiref_server, raw_pattern=r"\bwsgiref\.simple_server\b"),
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
        one_signature.server_name
        for one_signature in _SERVER_SIGNATURES
        if prefilter.contains_any_literal(lowered_source, one_signature.prefilter_literals)
        and one_signature.compiled_pattern.search(raw_source)
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
