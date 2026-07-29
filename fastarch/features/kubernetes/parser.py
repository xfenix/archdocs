import dataclasses
import typing

from fastarch.features.kubernetes import const, lookup, manifests


type _KindNames = tuple[str, ...]
type _ConfigurationPaths = tuple[tuple[manifests.ValuePath, str, str], ...]

_NAME_KEY: typing.Final = "name"
_KIND_PATH: typing.Final[manifests.ValuePath] = ("kind",)
_TRUE_VALUES: typing.Final = frozenset(("true", "yes", "on"))
_CONFIGURATION_SOURCE_PATHS: typing.Final[_ConfigurationPaths] = (
    (("configMapRef", _NAME_KEY), const.CONFIG_MAP_KIND, const.ENVIRONMENT_ATTACHMENT),
    (("configMapKeyRef", _NAME_KEY), const.CONFIG_MAP_KIND, const.ENVIRONMENT_ATTACHMENT),
    (("existingConfigMap",), const.CONFIG_MAP_KIND, const.ENVIRONMENT_ATTACHMENT),
    (("secretRef", _NAME_KEY), const.SECRET_KIND, const.ENVIRONMENT_ATTACHMENT),
    (("secretKeyRef", _NAME_KEY), const.SECRET_KIND, const.ENVIRONMENT_ATTACHMENT),
    (("existingSecret",), const.SECRET_KIND, const.ENVIRONMENT_ATTACHMENT),
    (("configMap", _NAME_KEY), const.CONFIG_MAP_KIND, const.VOLUME_ATTACHMENT),
    (("secret", "secretName"), const.SECRET_KIND, const.VOLUME_ATTACHMENT),
)


def _read_toggle(
    all_values: manifests.ManifestValues,
    toggle_path: manifests.ValuePath,
    kind_name: str,
    all_kinds: _KindNames,
    /,
) -> bool:
    toggle_value: typing.Final = lookup.read_first_value(all_values, toggle_path)
    if toggle_value:
        return toggle_value.lower() in _TRUE_VALUES
    return kind_name in all_kinds


def _read_amounts(all_values: manifests.ManifestValues, /, *resource_keys: str) -> const.ResourceAmounts:
    return const.ResourceAmounts(
        requested_amount=lookup.read_first_value(
            all_values,
            *[("resources", "requests", one_resource_key) for one_resource_key in resource_keys],
        ),
        limited_amount=lookup.read_first_value(
            all_values,
            *[("resources", "limits", one_resource_key) for one_resource_key in resource_keys],
        ),
    )


def _read_traffic(all_values: manifests.ManifestValues, all_kinds: _KindNames, /) -> const.TrafficFeatures:
    ingress_enabled: typing.Final = _read_toggle(all_values, ("ingress", "enabled"), const.INGRESS_KIND, all_kinds)
    return const.TrafficFeatures(
        ingress_enabled=ingress_enabled,
        ingress_hosts=lookup.read_values(all_values, ("hosts", "host"), ("rules", "host")) if ingress_enabled else (),
        ingress_tls_enabled=ingress_enabled and lookup.has_any_block(all_values, ("ingress", "tls"), ("spec", "tls")),
        service_type=lookup.read_first_value(all_values, ("service", "type"), ("spec", "type")),
        service_port=lookup.read_int_value(all_values, ("service", "port"), ("ports", "port")),
    )


def _read_scaling(all_values: manifests.ManifestValues, all_kinds: _KindNames, /) -> const.ScalingFeatures:
    plain_scaling: typing.Final = const.ScalingFeatures(
        workload_kind=next((one_kind for one_kind in all_kinds if one_kind in const.WORKLOAD_KINDS), ""),
        replica_count=lookup.read_int_value(all_values, ("replicaCount",), ("spec", "replicas")),
    )
    if not _read_toggle(all_values, ("autoscaling", "enabled"), const.AUTOSCALER_KIND, all_kinds):
        return plain_scaling
    return dataclasses.replace(
        plain_scaling,
        min_replicas=lookup.read_int_value(all_values, ("minReplicas",)),
        max_replicas=lookup.read_int_value(all_values, ("maxReplicas",)),
        target_cpu_utilization=lookup.read_int_value(
            all_values,
            ("targetCPUUtilizationPercentage",),
            ("target", "averageUtilization"),
        ),
    )


def _read_resources(all_values: manifests.ManifestValues, all_kinds: _KindNames, /) -> const.ResourceFeatures:
    return const.ResourceFeatures(
        cpu_amounts=_read_amounts(all_values, "cpu"),
        memory_amounts=_read_amounts(all_values, "memory"),
        gpu_amounts=_read_amounts(all_values, *const.GPU_RESOURCE_KEYS),
        persistence_enabled=_read_toggle(all_values, ("persistence", "enabled"), const.VOLUME_CLAIM_KIND, all_kinds)
        or lookup.has_any_block(all_values, ("volumeClaimTemplates",)),
        persistence_size=lookup.read_first_value(all_values, ("persistence", "size"), ("requests", "storage")),
    )


def _read_configuration(all_values: manifests.ManifestValues, /) -> tuple[const.ConfigurationSource, ...]:
    return tuple(
        dict.fromkeys(
            const.ConfigurationSource(
                source_kind=one_source_kind,
                source_name=one_source_name,
                attachment_kind=one_attachment_kind,
            )
            for one_value_path, one_source_kind, one_attachment_kind in _CONFIGURATION_SOURCE_PATHS
            for one_source_name in lookup.read_values(all_values, one_value_path)
        ),
    )


def find_kubernetes_features(raw_source: str) -> const.KubernetesFeatures:
    all_values: typing.Final = manifests.read_manifest_values(raw_source)
    all_kinds: typing.Final = lookup.read_values(all_values, _KIND_PATH)
    return const.KubernetesFeatures(
        traffic_features=_read_traffic(all_values, all_kinds),
        scaling_features=_read_scaling(all_values, all_kinds),
        resource_features=_read_resources(all_values, all_kinds),
        configuration_sources=_read_configuration(all_values),
    )
