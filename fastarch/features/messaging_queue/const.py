import dataclasses
import enum
import typing


@typing.final
class BrokersEnum(enum.Enum):
    RABBIT = "rabbit"
    KAFKA = "kafka"
    NATS = "nats"
    REDIS = "redis"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MQFeatures:
    consumers: bool
    producers: bool
    broker_names: list[str]
