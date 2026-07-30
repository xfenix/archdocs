import dataclasses
import enum
import types
import typing


@typing.final
class BrokersEnum(enum.Enum):
    rabbit_broker = "rabbit"
    kafka_broker = "kafka"
    nats_broker = "nats"
    redis_broker = "redis"


BROKER_CLASS_OF_NAME: typing.Final = types.MappingProxyType(
    {
        BrokersEnum.rabbit_broker: "RabbitBroker",
        BrokersEnum.kafka_broker: "KafkaBroker",
        BrokersEnum.nats_broker: "NatsBroker",
        BrokersEnum.redis_broker: "RedisBroker",
    },
)
# faststream names the destination differently per broker, and the decorators take it
# positionally, so a queue, a topic, a subject and a channel all end up in the same slot.
DESTINATION_KEYWORDS: typing.Final = ("queue", "topic", "subject", "channel", "stream", "list")


@typing.final
class MessageDirection(enum.Enum):
    consumed = "consumed"
    produced = "produced"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class BrokerFlow:
    broker_name: str
    consumes: bool
    produces: bool
    consumed_topics: tuple[str, ...] = ()
    produced_topics: tuple[str, ...] = ()


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MQFeatures:
    broker_flows: tuple[BrokerFlow, ...] = ()
