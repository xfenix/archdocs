"""Redis Cluster with the shared catalogue of the showcase service."""

import typing

from redis.cluster import ClusterNode, RedisCluster


CLUSTER_NODES: typing.Final = [ClusterNode("catalogue-one", 7000), ClusterNode("catalogue-two", 7001)]

cluster_client: typing.Final = RedisCluster(startup_nodes=CLUSTER_NODES, decode_responses=True)


def get_catalogue_item(sku: str) -> str | None:
    """Read a catalogue item from the cluster."""
    return cluster_client.get(sku)


def set_catalogue_item(sku: str, payload: str) -> None:
    """Write a catalogue item to the cluster."""
    cluster_client.set(sku, payload)
