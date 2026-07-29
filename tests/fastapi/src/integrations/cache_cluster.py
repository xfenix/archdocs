from redis.cluster import ClusterNode, RedisCluster


CLUSTER_NODES = [ClusterNode("localhost", 7000), ClusterNode("localhost", 7001)]

cluster_client = RedisCluster(startup_nodes=CLUSTER_NODES, decode_responses=True)


def get_shared_value(key: str) -> str | None:
    """Read a value from the cluster."""
    return cluster_client.get(key)


def set_shared_value(key: str, value: str) -> None:
    """Write a value to the cluster."""
    cluster_client.set(key, value)
