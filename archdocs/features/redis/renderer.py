import typing

from archdocs import diagram_model, settings
from archdocs.features.redis.const import RedisFeatures


_REDIS_NODE_LABEL: typing.Final = "redis"


def _build_redis_node(connection_type: str, node_suffix: int | str, /) -> diagram_model.DiagramNode:
    node_kind: typing.Final = f"{_REDIS_NODE_LABEL} {connection_type}" if connection_type else _REDIS_NODE_LABEL
    return diagram_model.build_diagram_node(
        f"redisdb_{connection_type}{node_suffix}" if connection_type else "redisdb",
        node_kind if node_suffix == "" else f"{node_kind} #{node_suffix}",
        diagram_model.NodeGroup.data_stores,
    )


def render_redis_features(
    service_node: diagram_model.DiagramNode,
    features_to_draw: RedisFeatures,
    /,
) -> tuple[diagram_model.DiagramEdge, ...]:
    if not features_to_draw.connection_type and not features_to_draw.async_used and not features_to_draw.retry_used:
        return ()
    properties_on_arrow: typing.Final = ", ".join(
        filter(
            None,
            [
                "async" if features_to_draw.async_used else "",
                "retry" if features_to_draw.retry_used else "",
            ],
        ),
    )
    if features_to_draw.connection_type not in ("sentinel", "cluster"):
        return (
            diagram_model.DiagramEdge(
                source_node=service_node,
                target_node=_build_redis_node("", ""),
                edge_label=properties_on_arrow,
            ),
        )
    return tuple(
        diagram_model.DiagramEdge(
            source_node=service_node,
            target_node=_build_redis_node(features_to_draw.connection_type or "", one_counter),
            edge_label=properties_on_arrow,
        )
        for one_counter in range(settings.VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION)
    )
