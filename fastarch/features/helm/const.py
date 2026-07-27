import dataclasses
import typing


LOAD_BALANCER_SERVICE_TYPE: typing.Final = "LoadBalancer"
NODE_PORT_SERVICE_TYPE: typing.Final = "NodePort"
INGRESS_MANIFEST_KIND: typing.Final = "Ingress"
AUTOSCALER_MANIFEST_KIND: typing.Final = "HorizontalPodAutoscaler"

CHART_MARKER_FILE_NAME: typing.Final = "Chart.yaml"
CHART_SEARCH_DIRS: typing.Final = ("deploy", "helm", "charts", ".helm")
PARENT_LOOKUP_DEPTH: typing.Final = 3
PROJECT_ROOT_MARKERS: typing.Final = (".git", "pyproject.toml", "setup.py", "setup.cfg")
NESTED_LOOKUP_PREFIXES: typing.Final = ("", "*/", "*/*/", "*/*/*/")
NESTED_LOOKUP_PATTERNS: typing.Final = tuple(
    f"{one_prefix}{CHART_MARKER_FILE_NAME}" for one_prefix in NESTED_LOOKUP_PREFIXES
)
PARENT_LOOKUP_PATTERNS: typing.Final = NESTED_LOOKUP_PATTERNS[:2]
MANIFEST_SEARCH_PATTERNS: typing.Final = (
    CHART_MARKER_FILE_NAME,
    "values.yaml",
    "values.yml",
    "templates/*.yaml",
    "templates/*.yml",
)


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ChartValueLine:
    block_name: str
    value_key: str
    raw_value: str


type ChartValueLines = tuple[ChartValueLine, ...]


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HelmChartFeatures:
    ingress_enabled: bool = False
    ingress_hosts: tuple[str, ...] = ()
    ingress_tls_enabled: bool = False
    service_type: str = ""
    replica_count: int = 0
    autoscaling_enabled: bool = False
    min_replicas: int = 0
    max_replicas: int = 0
    target_cpu_utilization: int = 0
