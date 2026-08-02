import dataclasses
import typing


CONFIG_MAP_KIND: typing.Final = "ConfigMap"
SECRET_KIND: typing.Final = "Secret"  # noqa: S105 — a manifest kind, not a credential
INGRESS_KIND: typing.Final = "Ingress"
AUTOSCALER_KIND: typing.Final = "HorizontalPodAutoscaler"
VOLUME_CLAIM_KIND: typing.Final = "PersistentVolumeClaim"
DEFAULT_WORKLOAD_KIND: typing.Final = "Deployment"
WORKLOAD_KINDS: typing.Final = frozenset((DEFAULT_WORKLOAD_KIND, "StatefulSet", "DaemonSet", "CronJob", "Job"))
EXPOSED_SERVICE_TYPES: typing.Final = frozenset(("LoadBalancer", "NodePort"))
ENVIRONMENT_ATTACHMENT: typing.Final = "env"
VOLUME_ATTACHMENT: typing.Final = "volume"
GPU_RESOURCE_KEYS: typing.Final = ("nvidia.com/gpu", "amd.com/gpu", "gpu")

REPOSITORY_MARKER_NAME: typing.Final = ".git"
PARENT_SEARCH_DEPTH: typing.Final = 2
TEMPLATES_DIR_NAME: typing.Final = "templates"
VALUES_FILE_STEM: typing.Final = "values"
MANIFEST_FILE_SUFFIXES: typing.Final = (".yaml", ".yml")


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ResourceAmounts:
    requested_amount: str = ""
    limited_amount: str = ""


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ConfigurationSource:
    source_kind: str
    source_name: str
    attachment_kind: str


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class TrafficFeatures:
    ingress_enabled: bool = False
    ingress_hosts: tuple[str, ...] = ()
    ingress_tls_enabled: bool = False
    service_type: str = ""
    service_port: int = 0


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ScalingFeatures:
    workload_kind: str = ""
    replica_count: int = 0
    min_replicas: int = 0
    max_replicas: int = 0
    target_cpu_utilization: int = 0


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class ResourceFeatures:
    cpu_amounts: ResourceAmounts = ResourceAmounts()
    memory_amounts: ResourceAmounts = ResourceAmounts()
    gpu_amounts: ResourceAmounts = ResourceAmounts()
    persistence_enabled: bool = False
    persistence_size: str = ""


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class KubernetesFeatures:
    traffic_features: TrafficFeatures = TrafficFeatures()
    scaling_features: ScalingFeatures = ScalingFeatures()
    resource_features: ResourceFeatures = ResourceFeatures()
    configuration_sources: tuple[ConfigurationSource, ...] = ()
