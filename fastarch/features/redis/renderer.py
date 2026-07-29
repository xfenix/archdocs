import typing

from fastarch import diagram_model, settings
from fastarch.features.redis.const import RedisFeatures


_REDIS_NODE_LABEL: typing.Final = "redis"


def _build_redis_node(node_suffix: int | str, /) -> diagram_model.DiagramNode:
    return diagram_model.build_diagram_node(
        f"redisdb{node_suffix}",
        _REDIS_NODE_LABEL if node_suffix == "" else f"{_REDIS_NODE_LABEL} #{node_suffix}",
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
                features_to_draw.connection_type if features_to_draw.cluster_or_sentinel else "",
            ],
        ),
    )
    return tuple(
        diagram_model.DiagramEdge(
            source_node=service_node,
            target_node=_build_redis_node(one_counter if features_to_draw.cluster_or_sentinel else ""),
            edge_label=properties_on_arrow,
        )
        for one_counter in range(settings.VALUE_FOR_MASS_CONNECTIONS_ILLUSTRATION)
    )
