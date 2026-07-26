import dataclasses
import typing


LOAD_BALANCER_SERVICE_TYPE: typing.Final = "LoadBalancer"
NODE_PORT_SERVICE_TYPE: typing.Final = "NodePort"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HelmChartFeatures:
    chart_detected: bool
    ingress_enabled: bool = False
    ingress_hosts: tuple[str, ...] = ()
    ingress_tls_enabled: bool = False
    service_type: str = ""
    replica_count: int = 0
    autoscaling_enabled: bool = False
    min_replicas: int = 0
    max_replicas: int = 0
    target_cpu_utilization: int = 0
