import dataclasses
import enum
import typing


@typing.final
class BrokersEnum(enum.Enum):
    rabbit = "rabbit"
    kafka = "kafka"
    nats = "nats"
    redis = "redis"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MQFeatures:
    consumers: bool
    producers: bool
    brokers: list[str]
