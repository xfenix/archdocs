import typing

from fastarch.features.helm import values
from fastarch.features.helm.const import (
    AUTOSCALER_MANIFEST_KIND,
    INGRESS_MANIFEST_KIND,
    ChartValueLines,
    HelmChartFeatures,
)


_INGRESS_BLOCK: typing.Final = "ingress"
_AUTOSCALING_BLOCK: typing.Final = "autoscaling"
_TRUE_VALUES: typing.Final = frozenset(("true", "yes", "on"))


def _read_feature_toggle(all_value_lines: ChartValueLines, block_name: str, kind_name: str, /) -> bool:
    toggle_value: typing.Final = values.read_first_value(all_value_lines, block_name, "enabled")
    if toggle_value:
        return toggle_value.lower() in _TRUE_VALUES
    return kind_name in values.read_values(all_value_lines, values.TOP_LEVEL_BLOCK, "kind")


def find_helm_features(raw_source: str) -> HelmChartFeatures:
    all_value_lines: typing.Final = values.read_chart_values(raw_source)
    scaling_enabled: typing.Final = _read_feature_toggle(all_value_lines, _AUTOSCALING_BLOCK, AUTOSCALER_MANIFEST_KIND)
    return HelmChartFeatures(
        ingress_enabled=_read_feature_toggle(all_value_lines, _INGRESS_BLOCK, INGRESS_MANIFEST_KIND),
        ingress_hosts=values.read_values(all_value_lines, _INGRESS_BLOCK, "host"),
        ingress_tls_enabled=bool(values.read_first_value(all_value_lines, _INGRESS_BLOCK, "secretName")),
        service_type=values.read_first_value(all_value_lines, "service", "type"),
        replica_count=values.read_int_value(all_value_lines, values.TOP_LEVEL_BLOCK, "replicaCount")
        or values.read_int_value(all_value_lines, "spec", "replicas"),
        autoscaling_enabled=scaling_enabled,
        min_replicas=values.read_int_value(all_value_lines, _AUTOSCALING_BLOCK, "minReplicas")
        if scaling_enabled
        else 0,
        max_replicas=values.read_int_value(all_value_lines, _AUTOSCALING_BLOCK, "maxReplicas")
        if scaling_enabled
        else 0,
        target_cpu_utilization=(
            values.read_int_value(all_value_lines, _AUTOSCALING_BLOCK, "targetCPUUtilizationPercentage")
            if scaling_enabled
            else 0
        ),
    )
