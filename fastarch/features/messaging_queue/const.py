import dataclasses
import enum


class BrokersEnum(enum.Enum):
    RABBIT = "rabbit"
    KAFKA = "kafka"
    NATS = "nats"
    REDIS = "redis"


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MQFeatures:
    consumers: bool
    producers: bool
    brokers: list[str]
