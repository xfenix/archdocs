import dataclasses
import enum
import typing


@typing.final
class BrokersEnum(enum.Enum):
    rabbit_broker = "rabbit"
    kafka_broker = "kafka"
    nats_broker = "nats"
    redis_broker = "redis"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MQFeatures:
    consumers: bool
    producers: bool
    broker_names: list[str]
