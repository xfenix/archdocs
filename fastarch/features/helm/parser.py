import re as py_re
import typing

from fastarch import settings
from fastarch.features.helm.const import HelmChartFeatures


# NOTE: settings.TYPICAL_RE_FLAGS enables re.DOTALL, so a bare `.` also matches newlines.
# YAML is line oriented, therefore every pattern below spells `[^\n]` explicitly.
#
# A top level YAML key always starts at column 0 and its body is the following run of
# blank or indented lines. That run stops at the next column 0 line, which includes the
# `---` document separator and the first key of the next concatenated file, so blocks
# never bleed from one chart file into another.
_TOP_LEVEL_BLOCK_TEMPLATE: typing.Final = r"^{block_name}:[^\n]*\n(?P<block_body>(?:[ \t]+[^\n]*\n|[ \t]*\n)*)"

_INGRESS_BLOCK_PATTERN: typing.Final = py_re.compile(
    _TOP_LEVEL_BLOCK_TEMPLATE.format(block_name="ingress"),
    flags=settings.TYPICAL_RE_FLAGS,
)
_SERVICE_BLOCK_PATTERN: typing.Final = py_re.compile(
    _TOP_LEVEL_BLOCK_TEMPLATE.format(block_name="service"),
    flags=settings.TYPICAL_RE_FLAGS,
)
_AUTOSCALING_BLOCK_PATTERN: typing.Final = py_re.compile(
    _TOP_LEVEL_BLOCK_TEMPLATE.format(block_name="autoscaling"),
    flags=settings.TYPICAL_RE_FLAGS,
)
_ENABLED_TRUE_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]+enabled:[ \t]*[\"']?(?:true|yes|on)[\"']?[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_ENABLED_FALSE_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]+enabled:[ \t]*[\"']?(?:false|no|off)[\"']?[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_INGRESS_HOST_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*-?[ \t]*host:[ \t]*[\"']?(?P<ingress_host>[A-Za-z0-9*][A-Za-z0-9.\-]*)[\"']?[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_INGRESS_TLS_PATTERN: typing.Final = py_re.compile(
    # `secretName` shows up both as a plain key and as the first key of a list item.
    # Only ever searched inside the `ingress:` block: a `secretName` belonging to some
    # other resource must not flip the entrypoint edge to HTTPS.
    r"^[ \t]*-?[ \t]*secretName:[ \t]*\S",
    flags=settings.TYPICAL_RE_FLAGS,
)
_SERVICE_TYPE_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*type:[ \t]*[\"']?(?P<service_type>LoadBalancer|NodePort|ClusterIP|ExternalName)\b",
    flags=settings.TYPICAL_RE_FLAGS,
)
_REPLICA_COUNT_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*replicaCount:[ \t]*(?P<replica_count>\d+)[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_LITERAL_REPLICAS_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*replicas:[ \t]*(?P<literal_replicas>\d+)[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_INGRESS_KIND_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*kind:[ \t]*[\"']?Ingress[\"']?[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_AUTOSCALER_KIND_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*kind:[ \t]*[\"']?HorizontalPodAutoscaler[\"']?[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_MIN_REPLICAS_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*minReplicas:[ \t]*(?P<min_replicas>\d+)[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_MAX_REPLICAS_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*maxReplicas:[ \t]*(?P<max_replicas>\d+)[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_TARGET_CPU_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*(?:targetCPUUtilizationPercentage|averageUtilization):[ \t]*(?P<target_cpu>\d+)[ \t]*$",
    flags=settings.TYPICAL_RE_FLAGS,
)
_CHART_MARKER_PATTERN: typing.Final = py_re.compile(
    r"^apiVersion:[ \t]*\S|^replicaCount:[ \t]*\S",
    flags=settings.TYPICAL_RE_FLAGS,
)


def _extract_block_body(block_pattern: py_re.Pattern[str], raw_source: str) -> str:
    block_match: typing.Final = block_pattern.search(raw_source)
    return block_match.group("block_body") if block_match else ""


def _extract_named_group(value_pattern: py_re.Pattern[str], raw_source: str, group_name: str, /) -> str:
    value_match: typing.Final = value_pattern.search(raw_source)
    return value_match.group(group_name) if value_match else ""


def _extract_positive_int(value_pattern: py_re.Pattern[str], raw_source: str, group_name: str, /) -> int:
    raw_value: typing.Final = _extract_named_group(value_pattern, raw_source, group_name)
    return int(raw_value) if raw_value else 0


def _extract_replica_count(raw_source: str) -> int:
    # `values.yaml` holds the literal number, templates only hold `{{ .Values.replicaCount }}`.
    declared_replica_count: typing.Final = _extract_positive_int(_REPLICA_COUNT_PATTERN, raw_source, "replica_count")
    if declared_replica_count:
        return declared_replica_count
    return _extract_positive_int(_LITERAL_REPLICAS_PATTERN, raw_source, "literal_replicas")


def _extract_ingress_hosts(raw_source: str) -> tuple[str, ...]:
    # Hosts repeat between the `hosts:` and `tls:` sections, dict.fromkeys dedupes in chart order.
    # Templated values such as `host: {{ .host | quote }}` never match, which is intended:
    # a literal `{{` inside a mermaid edge label is itself a syntax error.
    return tuple(dict.fromkeys(_INGRESS_HOST_PATTERN.findall(raw_source)))


def _read_feature_toggle(values_block_body: str, manifest_kind_pattern: py_re.Pattern[str], raw_source: str, /) -> bool:
    # `enabled` is tri state. A chart template carries `kind: Ingress` inside a
    # `{{- if .Values.ingress.enabled }}` guard, so its presence proves the chart
    # supports the feature, never that the values switched it on. An explicit
    # `enabled: false` therefore wins, and the manifest is only a fallback for
    # charts that omit the toggle entirely.
    if _ENABLED_TRUE_PATTERN.search(values_block_body):
        return True
    if _ENABLED_FALSE_PATTERN.search(values_block_body):
        return False
    return bool(manifest_kind_pattern.search(raw_source))


def find_helm_features(raw_source: str) -> HelmChartFeatures:
    if not _CHART_MARKER_PATTERN.search(raw_source):
        return HelmChartFeatures(chart_detected=False)
    ingress_block_body: typing.Final = _extract_block_body(_INGRESS_BLOCK_PATTERN, raw_source)
    service_block_body: typing.Final = _extract_block_body(_SERVICE_BLOCK_PATTERN, raw_source)
    autoscaling_block_body: typing.Final = _extract_block_body(_AUTOSCALING_BLOCK_PATTERN, raw_source)
    return HelmChartFeatures(
        chart_detected=True,
        ingress_enabled=_read_feature_toggle(ingress_block_body, _INGRESS_KIND_PATTERN, raw_source),
        ingress_hosts=_extract_ingress_hosts(raw_source),
        ingress_tls_enabled=bool(_INGRESS_TLS_PATTERN.search(ingress_block_body)),
        service_type=_extract_named_group(_SERVICE_TYPE_PATTERN, service_block_body, "service_type"),
        replica_count=_extract_replica_count(raw_source),
        autoscaling_enabled=_read_feature_toggle(autoscaling_block_body, _AUTOSCALER_KIND_PATTERN, raw_source),
        min_replicas=_extract_positive_int(_MIN_REPLICAS_PATTERN, autoscaling_block_body, "min_replicas"),
        max_replicas=_extract_positive_int(_MAX_REPLICAS_PATTERN, autoscaling_block_body, "max_replicas"),
        target_cpu_utilization=_extract_positive_int(_TARGET_CPU_PATTERN, autoscaling_block_body, "target_cpu"),
    )
